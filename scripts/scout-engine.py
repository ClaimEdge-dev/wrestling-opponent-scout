#!/usr/bin/env python3
"""
Wrestling Opponent Scout Engine
Core engine for opponent scouting, matchup analysis, and database operations.
Integrates with Neon Postgres for persistent wrestler profiles.

Usage:
    python scout-engine.py --scout "Wrestler A" --opponent "Wrestler B" --division 10UD
    python scout-engine.py --bracket bracket.json --focus "Chase Krapil"
    python scout-engine.py --update-ego --match "A vs B" --result W --score "2-1"
    python scout-engine.py --db-stats
    python scout-engine.py --seed-bracket bracket.json --focus "Chase Krapil"
"""

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import logging

# Database integration - uses psycopg2 if available
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_DB = True
except ImportError:
    HAS_DB = False
    print("WARNING: psycopg2 not installed. Database features disabled.")
    print("Install with: pip install psycopg2-binary")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
TIER_RANKS = {"ELITE": 5, "NATIONAL": 4, "STATE": 3, "REGIONAL": 2, "LOCAL": 1, "UNKNOWN": 0}
TIER_STARTING_EGO = {"ELITE": 1800, "NATIONAL": 1650, "STATE": 1500, "REGIONAL": 1350, "LOCAL": 1200, "UNKNOWN": 1300}
TIER_K_FACTORS = {"ELITE": 24, "NATIONAL": 28, "STATE": 32, "REGIONAL": 36, "LOCAL": 40, "UNKNOWN": 36}
STATE_TIER_MULTIPLIERS = {"IL": 1.2, "OH": 1.2, "PA": 1.2, "NJ": 1.2, "MN": 1.2,
                            "IN": 1.0, "MI": 1.0, "WI": 1.0, "IA": 1.0, "MO": 1.0}
WIN_TYPE_MODIFIERS = {"Fall": 0.3, "TF": 0.2, "MD": 0.1, "Dec": 0.0, "SV": 0.0}
PILLAR_WEIGHTS = {"P1": 0.35, "P2": 0.30, "P3": 0.25, "P4": 0.10}


@dataclass
class WrestlerProfile:
    """Represents a wrestler's complete profile."""
    name: str
    team: str
    state: str
    division: str
    primary_weight: int = 0
    secondary_weights: List[int] = field(default_factory=list)
    total_wins: int = 0
    total_losses: int = 0
    pin_rate: float = 0.0
    tech_fall_rate: float = 0.0
    major_rate: float = 0.0
    national_titles: int = 0
    state_titles: int = 0
    state_placements: int = 0
    regional_titles: int = 0
    credential_tier: str = "UNKNOWN"
    four_pillar_p1: float = 0.0  # Result Strength
    four_pillar_p2: float = 0.0  # Style Profile
    four_pillar_p3: float = 0.0  # Competition Level
    four_pillar_p4: float = 0.0  # Weight Fit
    ego_rating: int = 1500
    momentum_index: float = 50.0
    notes: str = ""
    sources: List[Dict] = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        total = self.total_wins + self.total_losses
        return self.total_wins / total if total > 0 else 0.0

    @property
    def composite_score(self) -> float:
        return (self.four_pillar_p1 * PILLAR_WEIGHTS["P1"] +
                self.four_pillar_p2 * PILLAR_WEIGHTS["P2"] +
                self.four_pillar_p3 * PILLAR_WEIGHTS["P3"] +
                self.four_pillar_p4 * PILLAR_WEIGHTS["P4"])


class CredentialClassifier:
    """Classifies wrestlers into credential tiers based on achievements."""

    @staticmethod
    def auto_classify(wins: int, losses: int, national_places: List[int] = None,
                      state_places: List[int] = None) -> str:
        national_places = national_places or []
        state_places = state_places or []

        if national_places and min(national_places) <= 3:
            return "ELITE"
        if national_places and min(national_places) <= 8:
            return "NATIONAL"
        if state_places and min(state_places) <= 4:
            return "STATE"
        if wins >= 50:
            return "REGIONAL"
        if wins >= 10:
            return "LOCAL"
        return "UNKNOWN"

    @staticmethod
    def apply_state_multiplier(base_score: float, state: str) -> float:
        return base_score * STATE_TIER_MULTIPLIERS.get(state, 0.9)


class MatchupCalculator:
    """Calculates win probabilities and matchup analysis."""

    @staticmethod
    def win_probability(wrestler_a: WrestlerProfile, wrestler_b: WrestlerProfile,
                        h2h_history: List[Dict] = None) -> Dict:
        h2h_history = h2h_history or []

        # Step 1: Pillar difference
        pillar_diff = (
            (wrestler_a.four_pillar_p1 - wrestler_b.four_pillar_p1) * PILLAR_WEIGHTS["P1"] +
            (wrestler_a.four_pillar_p2 - wrestler_b.four_pillar_p2) * PILLAR_WEIGHTS["P2"] +
            (wrestler_a.four_pillar_p3 - wrestler_b.four_pillar_p3) * PILLAR_WEIGHTS["P3"] +
            (wrestler_a.four_pillar_p4 - wrestler_b.four_pillar_p4) * PILLAR_WEIGHTS["P4"]
        )

        # Step 2: EGO contribution
        ego_diff = (wrestler_a.ego_rating - wrestler_b.ego_rating) / 400
        ego_prob = 1 / (1 + 10 ** (-ego_diff))

        # Step 3: Head-to-head
        h2h_bonus = 0.0
        if h2h_history:
            a_wins = sum(1 for m in h2h_history if m.get("winner") == wrestler_a.name)
            total = len(h2h_history)
            h2h_bonus = (a_wins / total - 0.5) * 0.2 if total > 0 else 0.0

        # Combined probability
        combined = pillar_diff * 0.6 + ego_prob * 0.3 + h2h_bonus * 0.1
        prob = 1 / (1 + math.exp(-combined * 1.5))
        prob = max(0.05, min(0.95, prob))

        # Confidence level
        data_points = sum(1 for p in [wrestler_a.four_pillar_p1, wrestler_b.four_pillar_p1] if p > 0)
        confidence = "HIGH" if data_points >= 6 else "MEDIUM" if data_points >= 3 else "LOW"

        # Upset risk
        upset_risk = "HIGH" if abs(prob - 0.5) < 0.15 else "MODERATE" if abs(prob - 0.5) < 0.3 else "LOW"

        return {
            "wrestler_a": wrestler_a.name,
            "wrestler_b": wrestler_b.name,
            "win_probability": round(prob * 100, 1),
            "confidence": confidence,
            "upset_risk": upset_risk,
            "pillar_difference": round(pillar_diff, 3),
            "ego_contribution": round(ego_prob, 3),
            "h2h_contribution": round(h2h_bonus, 3)
        }

    @staticmethod
    def update_ego(winner: WrestlerProfile, loser: WrestlerProfile,
                   win_type: str = "Dec") -> Tuple[int, int]:
        margin_mod = WIN_TYPE_MODIFIERS.get(win_type, 0.0)
        expected_w = 1 / (1 + 10 ** ((loser.ego_rating - winner.ego_rating) / 400))
        expected_l = 1 / (1 + 10 ** ((winner.ego_rating - loser.ego_rating) / 400))

        k_w = TIER_K_FACTORS.get(winner.credential_tier, 32)
        k_l = TIER_K_FACTORS.get(loser.credential_tier, 32)

        new_winner_ego = int(winner.ego_rating + k_w * (1 + margin_mod - expected_w))
        new_loser_ego = int(loser.ego_rating + k_l * (0 - margin_mod - expected_l))

        new_winner_ego = max(800, min(2400, new_winner_ego))
        new_loser_ego = max(800, min(2400, new_loser_ego))

        return new_winner_ego, new_loser_ego


class DatabaseManager:
    """Manages Neon Postgres database operations."""

    def __init__(self, connection_string: str = None):
        self.conn_string = connection_string or os.getenv("DATABASE_URL")
        self.conn = None

    def connect(self):
        if not HAS_DB or not self.conn_string:
            logger.warning("Database not available")
            return False
        try:
            self.conn = psycopg2.connect(self.conn_string)
            return True
        except Exception as e:
            logger.error(f"DB connection failed: {e}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()

    def get_wrestler(self, name: str, division: str = None) -> Optional[WrestlerProfile]:
        if not self.conn:
            return None
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                if division:
                    cur.execute("SELECT * FROM wrestler_profiles WHERE name = %s AND division = %s", (name, division))
                else:
                    cur.execute("SELECT * FROM wrestler_profiles WHERE name = %s", (name,))
                row = cur.fetchone()
                if row:
                    return self._row_to_profile(row)
        except Exception as e:
            logger.error(f"DB query failed: {e}")
        return None

    def _row_to_profile(self, row: Dict) -> WrestlerProfile:
        return WrestlerProfile(
            name=row["name"],
            team=row.get("team", ""),
            state=row.get("state", ""),
            division=row.get("division", ""),
            primary_weight=row.get("primary_weight", 0) or 0,
            credential_tier=row.get("credential_tier", "UNKNOWN"),
            total_wins=row.get("total_wins", 0) or 0,
            total_losses=row.get("total_losses", 0) or 0,
            ego_rating=row.get("ego_rating", 1500) or 1500,
            four_pillar_p1=float(row.get("four_pillar_p1", 0) or 0),
            four_pillar_p2=float(row.get("four_pillar_p2", 0) or 0),
            four_pillar_p3=float(row.get("four_pillar_p3", 0) or 0),
            four_pillar_p4=float(row.get("four_pillar_p4", 0) or 0),
            notes=row.get("notes", "") or ""
        )

    def save_matchup(self, wrestler_a_id: int, wrestler_b_id: int,
                     result: Dict, event_id: int = None) -> bool:
        if not self.conn:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO matchup_history 
                    (wrestler_a_id, wrestler_b_id, win_probability, confidence, 
                     upset_risk, event_id, calculated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (wrestler_a_id, wrestler_b_id, result["win_probability"],
                      result["confidence"], result["upset_risk"], event_id))
                self.conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save matchup: {e}")
            return False


class ReportGenerator:
    """Generates scouting reports in markdown and HTML."""

    @staticmethod
    def generate_matchup_report(wrestler_a: WrestlerProfile,
                                wrestler_b: WrestlerProfile,
                                result: Dict) -> str:
        lines = [
            f"# Matchup Report: {wrestler_a.name} vs {wrestler_b.name}",
            "",
            f"**Event:** NUWAY Rumble 2026 | **Weight:** {wrestler_a.primary_weight} lbs | **Division:** {wrestler_a.division}",
            "",
            "## Win Probability",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| {wrestler_a.name} Win % | **{result['win_probability']}%** |",
            f"| Confidence | {result['confidence']} |",
            f"| Upset Risk | {result['upset_risk']} |",
            "",
            "## Wrestler Profiles",
            "",
            f"### {wrestler_a.name} ({wrestler_a.team}, {wrestler_a.state})",
            f"- Credential Tier: {wrestler_a.credential_tier}",
            f"- EGO Rating: {wrestler_a.ego_rating}",
            f"- Record: {wrestler_a.total_wins}-{wrestler_a.total_losses}",
            f"- Pillar Scores: P1={wrestler_a.four_pillar_p1}, P2={wrestler_a.four_pillar_p2}, P3={wrestler_a.four_pillar_p3}, P4={wrestler_a.four_pillar_p4}",
            "",
            f"### {wrestler_b.name} ({wrestler_b.team}, {wrestler_b.state})",
            f"- Credential Tier: {wrestler_b.credential_tier}",
            f"- EGO Rating: {wrestler_b.ego_rating}",
            f"- Record: {wrestler_b.total_wins}-{wrestler_b.total_losses}",
            f"- Pillar Scores: P1={wrestler_b.four_pillar_p1}, P2={wrestler_b.four_pillar_p2}, P3={wrestler_b.four_pillar_p3}, P4={wrestler_b.four_pillar_p4}",
            "",
            "## Analysis",
            "",
            f"- Pillar Difference: {result['pillar_difference']}",
            f"- EGO Contribution: {result['ego_contribution']}",
            f"- H2H Contribution: {result['h2h_contribution']}",
            "",
            "---",
            "*All probabilities are ESTIMATES based on available data. Actual results may vary.*"
        ]
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Wrestling Opponent Scout Engine")
    parser.add_argument("--scout", help="Scout wrestler A")
    parser.add_argument("--opponent", help="Against wrestler B")
    parser.add_argument("--division", default="10U")
    parser.add_argument("--bracket", help="Bracket JSON file")
    parser.add_argument("--focus", help="Focus wrestler name")
    parser.add_argument("--db-stats", action="store_true", help="Show DB stats")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    parser.add_argument("--update-ego", action="store_true", help="Update EGO ratings")
    parser.add_argument("--match", help="Match result (A vs B)")
    parser.add_argument("--result", choices=["W", "L"])
    parser.add_argument("--score", help="Match score (e.g., 2-1)")
    parser.add_argument("--win-type", default="Dec", choices=["Fall", "TF", "MD", "Dec", "SV"])

    args = parser.parse_args()

    if args.demo:
        # Run a demo matchup
        chase = WrestlerProfile(
            name="Chase Krapil", team="Ascend Wrestling Academy", state="MI",
            division="10U", primary_weight=75, total_wins=18, total_losses=11,
            credential_tier="LOCAL", ego_rating=1350,
            four_pillar_p1=2.5, four_pillar_p2=3.0, four_pillar_p3=2.0, four_pillar_p4=3.5
        )
        opponent = WrestlerProfile(
            name="Jack Gorman", team="Maverick Elite", state="WI",
            division="10U", primary_weight=75, total_wins=253, total_losses=34,
            credential_tier="NATIONAL", ego_rating=1700,
            four_pillar_p1=4.5, four_pillar_p2=4.0, four_pillar_p3=4.5, four_pillar_p4=3.0
        )
        calc = MatchupCalculator()
        result = calc.win_probability(chase, opponent)
        report = ReportGenerator.generate_matchup_report(chase, opponent, result)
        print(report)
        return

    if args.bracket and args.focus:
        # Load bracket and generate scouting report
        with open(args.bracket) as f:
            bracket = json.load(f)
        print(f"Loaded bracket with {len(bracket.get('75', []))} wrestlers at 75 lbs")
        print(f"Loaded bracket with {len(bracket.get('80', []))} wrestlers at 80 lbs")
        print(f"Focus: {args.focus}")
        return

    if args.db_stats:
        db = DatabaseManager()
        if db.connect():
            print("Database connected successfully")
            db.close()
        else:
            print("Database connection failed")
        return

    parser.print_help()


if __name__ == "__main__":
    main()

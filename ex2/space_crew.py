from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: List[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission_rules(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        leaders = (Rank.COMMANDER, Rank.CAPTAIN)
        has_leader = any(m.rank in leaders for m in self.crew)
        if not has_leader:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            exp_count = sum(1 for m in self.crew if m.years_experience >= 5)
            if exp_count / len(self.crew) < 0.5:
                raise ValueError(
                    "Long missions (> 365 days) need 50% experienced "
                    "crew (5+ years)"
                )

        if any(not m.is_active for m in self.crew):
            raise ValueError("All crew members must be active")

        return self


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 41)

    c1 = CrewMember(
        member_id="C001",
        name="Sarah Connor",
        rank=Rank.COMMANDER,
        age=45,
        specialization="Mission Command",
        years_experience=15,
    )
    c2 = CrewMember(
        member_id="C002",
        name="John Smith",
        rank=Rank.LIEUTENANT,
        age=32,
        specialization="Navigation",
        years_experience=6,
    )
    c3 = CrewMember(
        member_id="C003",
        name="Alice Johnson",
        rank=Rank.OFFICER,
        age=28,
        specialization="Engineering",
        years_experience=3,
    )

    try:
        mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2024, 10, 23, 8, 0, 0),
            duration_days=900,
            crew=[c1, c2, c3],
            budget_millions=2500.0,
        )
        print("Valid mission created:")
        print(f"Mission: {mission.mission_name}")
        print(f"ID: {mission.mission_id}")
        print(f"Destination: {mission.destination}")
        print(f"Duration: {mission.duration_days} days")
        print(f"Budget: ${mission.budget_millions}M")
        print(f"Crew size: {len(mission.crew)}")
        print("Crew members:")
        for member in mission.crew:
            print(
                f"- {member.name} ({member.rank.value})-"
                f" {member.specialization}"
            )
    except ValidationError as e:
        print(f"Unexpected validation error: {e}")

    print("=" * 41)
    print("Expected validation error:")

    c4 = CrewMember(
        member_id="C004",
        name="Bob Vance",
        rank=Rank.OFFICER,
        age=40,
        specialization="Cargo",
        years_experience=12,
    )
    try:
        SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Cargo Transport",
            destination="Mars",
            launch_date=datetime(2024, 10, 23, 8, 0, 0),
            duration_days=900,
            crew=[c4],
            budget_millions=150.0,
        )
    except ValidationError as e:
        for error in e.errors():
            print(error["msg"])


if __name__ == "__main__":
    main()

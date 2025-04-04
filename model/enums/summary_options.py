from enum import Enum

# 추후 추가 옵션 추가 예정
class SummaryOption(str, Enum):
    Project = "ProjectSummary"
    Package = "DirectorySummary"

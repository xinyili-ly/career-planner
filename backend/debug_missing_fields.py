"""调试：验证 _compute_missing_fields 在完整 intake_data 下的行为"""
import sys
sys.path.insert(0, "app")

from main import (
    _compute_missing_fields,
    _field_missing,
    _is_explicit_none,
    _get_path,
    _CORE_FIELDS,
    _OPTIONAL_FIELDS,
)

# 模拟用户发来的完整 intake_data（与 start_from_profile 返回值一致）
intake_data = {
    "basic_info": {
        "name": "李奕昕",
        "gender": "男",
        "education_level": "本科",
        "major": "软工",
        "graduation_year": 2028,
    },
    "competencies": {
        "professional_skills": {
            "keywords": ["java", "python", "c语言", "c++", "mysql", "springbook", "git"],
        },
        "certificate_requirements": {"items": []},
        "innovation_capability": {"score": 0, "evidence": ""},
        "learning_capability": {"score": 0, "evidence": ""},
        "stress_resistance": {"score": 0, "evidence": ""},
        "communication_skills": {"score": 0, "evidence": ""},
        "internship_experience": {"history": [], "evaluation": ""},
    },
    "career_intent": {
        "job_preferences": ["后端开发岗位"],
        "target_cities": ["北京"],
        "expected_salary": "50k",
    },
    "experiences": {
        "main_courses": [],
        "projects": [],
        "awards": [],
        "campus_experience": None,
    },
}

print("=== _field_missing 逐字段检查 ===")
for f in _CORE_FIELDS:
    v = _get_path(intake_data, f)
    result = _field_missing(intake_data, f)
    print(f"  {f}: value={repr(v)}, missing={result}")

print("\n=== _compute_missing_fields 结果 ===")
core, optional, warnings = _compute_missing_fields(intake_data)
print(f"  core_missing: {core}")
print(f"  optional_missing: {optional}")
print(f"  warnings: {warnings}")

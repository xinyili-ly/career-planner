"""
完整调试：模拟 start_from_profile 的全流程，追踪 missing_fields 的来源
"""
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
from models.student_profile import StudentProfile, BasicInfo, CareerIntent, CompetencyItem, SkillCompetency, CertificateCompetency, InternshipCompetency, CoreCompetencies, ProjectExperience, Experiences
from pydantic import ValidationError

# === 场景1：模拟用户实际传进来的 student_profile（可能字段不全）===
print("=" * 60)
print("场景1：student_profile 部分字段缺失")
print("=" * 60)
try:
    profile1 = StudentProfile(
        basic_info=BasicInfo(
            name="李奕昕",
            gender="男",
            university="",          # 空字符串
            major="软工",
            education_level="本科",
            graduation_year=2028,
        ),
        career_intent=CareerIntent(
            expected_salary="50k",
            job_preferences=["后端开发岗位"],
            target_cities=["北京"],
        ),
        competencies=CoreCompetencies(
            professional_skills=SkillCompetency(
                score=5,
                evidence="熟悉 Java/Python",
                keywords=["java", "python"],
            ),
            certificate_requirements=CertificateCompetency(score=0, items=[], missing=[]),
            innovation_capability=CompetencyItem(score=0, evidence=""),
            learning_capability=CompetencyItem(score=0, evidence=""),
            stress_resistance=CompetencyItem(score=0, evidence=""),
            communication_skills=CompetencyItem(score=0, evidence=""),
            internship_experience=InternshipCompetency(score=0, history=[], evaluation=""),
        ),
        experiences=Experiences(
            projects=[],
            awards=[],
            main_courses=[],
        ),
    )
    print("✓ StudentProfile 构造成功")
except ValidationError as e:
    print(f"✗ StudentProfile 校验失败: {e}")
    sys.exit(1)

# === 场景2：university 为空字符串时 _field_missing 的判定 ===
print("\n=== _field_missing 对空字符串的判定 ===")
for f in _CORE_FIELDS:
    v = _get_path(profile1.model_dump(), f)
    result = _field_missing(profile1.model_dump(), f)
    print(f"  {f}: value={repr(v)}, missing={result}")

# === 场景3：_intake_data_from_student_profile 构造的值 ===
from main import _intake_data_from_student_profile
intake_data = _intake_data_from_student_profile(profile1)
print("\n=== _intake_data_from_student_profile 构造结果 ===")
for f in _CORE_FIELDS:
    v = _get_path(intake_data, f)
    result = _field_missing(intake_data, f)
    status = "✓" if not result else "✗ MISSING"
    print(f"  {status} {f}: value={repr(v)}, missing={result}")

# === 场景4：_compute_missing_fields 最终结果 ===
core, optional, warnings = _compute_missing_fields(intake_data)
print(f"\n=== _compute_missing_fields 最终结果 ===")
print(f"  core_missing:     {core}")
print(f"  optional_missing:  {optional}")
print(f"  warnings:          {warnings}")

# === 场景5：模拟 _start_intake_session 第一轮选题 ===
from main import _pick_templates_for_missing, _QUESTION_TEMPLATES
missing_fields = core if core else optional
print(f"\n=== _pick_templates_for_missing 参数 ===")
print(f"  missing_fields = {missing_fields}")
print(f"  asked_fields   = []")
templates = _pick_templates_for_missing(missing_fields, asked_fields=[])
print(f"  选中 {len(templates)} 个模板:")
for t in templates:
    print(f"    - {t.get('template_id')}: {t.get('target_fields')}")

print("\n=== 结论 ===")
if core:
    print(f"✗ BUG: core_missing 不应为空！")
    print(f"  问题字段: {core}")
else:
    print(f"✓ 正常: core_missing 为空（核心字段已填），第一轮应问可选字段")

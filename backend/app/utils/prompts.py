RESUME_PARSE_PROMPT = """
# Role
你是一个严格的 JSON 数据提取助手，专门将简历文本转换为标准化的学生画像 JSON。

# Task
请从简历原文中提取信息，输出符合以下 JSON Schema 的结构化数据。

# Output JSON Schema (必须严格遵循)
{
  "basic_info": {
    "name": "姓名（必填）",
    "gender": "性别：男/女/其他/不便透露（无则填null）",
    "university": "毕业院校（无则填null）",
    "major": "专业（必填）",
    "education_level": "学历层次：本科/硕士/博士（必填）",
    "graduation_year": 毕业年份，如 2025（无则填null）
  },
  "career_intent": {
    "expected_salary": "期望薪资范围（无则填null）",
    "job_preferences": ["偏好岗位列表（无则空列表）"],
    "target_cities": ["意向城市列表（无则空列表）"]
  },
  "competencies": {
    "professional_skills": {
      "score": 0-10整数,
      "evidence": "评分依据",
      "keywords": ["技能关键词列表"],
      "gap_analysis": "能力差距分析（无则null）"
    },
    "certificate_requirements": {
      "score": 0-10整数,
      "items": ["已获证书列表"],
      "missing": ["缺失的关键证书列表"]
    },
    "innovation_capability": {
      "score": 0-10整数,
      "evidence": "评分依据"
    },
    "learning_capability": {
      "score": 0-10整数,
      "evidence": "评分依据"
    },
    "stress_resistance": {
      "score": 0-10整数,
      "evidence": "评分依据"
    },
    "communication_skills": {
      "score": 0-10整数,
      "evidence": "评分依据"
    },
    "internship_experience": {
      "score": 0-10整数,
      "history": [{"company": "公司名", "position": "职位", "duration": "时长"}],
      "evaluation": "实习质量评价（无则null）"
    }
  },
  "experiences": {
    "projects": [{"name": "项目名", "role": "角色", "tech_stack": ["技术栈"], "achievement": "成果"}],
    "awards": ["奖项列表"],
    "main_courses": ["主修课程列表"],
    "campus_experience": "校园经历（无则null）",
    "social_practice": "社会实践（无则null）"
  },
  "personality": {
    "mbti": "MBTI类型（无则null）",
    "strengths": ["优势列表"],
    "weaknesses": ["劣势列表"]
  }
}

# 评分标准
1. **专业技能**：有2门以上核心语言+项目经验=7-10分；仅熟悉1门=4-6分；仅罗列名词=1-3分
2. **证书**：2本以上高含金量证书=7-10分；1本=4-6分；无=1-3分
3. **创新能力**：省部级以上奖项/专利=7-10分；校级=4-6分；无=1-3分
4. **学习能力**：有自学闭环+导师评价=7-10分；按部就班=4-6分；无=1-3分
5. **抗压能力**：独立完成高压任务=7-10分；有大型活动经历=4-6分；无=1-3分
6. **沟通能力**：跨团队协作+推动落地=7-10分；有答辩演讲=4-6分；无=1-3分
7. **实习能力**：大厂实习=7-10分；普通实习=4-6分；无=1-3分

# Rules
1. 所有必填字段（name, major, education_level）必须填写
2. 可选字段无信息时使用 null（字符串）或 []（列表）或 0（数字）
3. 评分必须是 0-10 的整数
4. 只输出 JSON，不要有其他文字

---
待解析简历原文：
{resume_text}
"""

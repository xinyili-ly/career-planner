# 全维学生就业能力画像设计方案 (Student Profile Schema)

为了支撑赛题要求的“职业生涯发展报告”生成（包括路径规划、行动计划等），现有的学生画像（仅包含7大维度）确实过于单薄。我们需要一个更立体的画像结构，不仅记录“现在有什么”，还要记录“想去哪里”和“过去做过什么”。

## 1. 核心设计理念
画像将分为三层结构：
1.  **基础层 (The Past)**: 学历、背景、已获证书。
2.  **能力层 (The Present)**: 7大维度能力评估（与岗位画像对齐）。
3.  **意愿层 (The Future)**: 职业兴趣、期望行业、发展目标（用于生成个性化报告）。

---

## 2. 详细数据结构定义

```json
{
  // --- 1. 基础信息 (Basic Info) ---
  "basic_info": {
    "name": "张三",
    "university": "某某理工大学",
    "major": "计算机科学与技术",
    "education_level": "本科",
  },

  // --- 2. 职业意愿 (Career Intent) - 用于报告生成 ---
  "career_intent": {
    "target_industries": ["互联网", "人工智能", "新能源"],
    "expected_salary": "12k-15k",
    "job_preferences": ["后端开发", "算法工程师"], // 偏好岗位
    "values": ["技术成长", "工作生活平衡"] // 职业价值观，用于匹配企业文化
  },

  // --- 3. 核心能力画像 (Core Competencies) - 与岗位画像严格对齐 ---
  "competencies": {
    "professional_skills": {
      "score": 85, // 0-100 量化分
      "keywords": ["Python", "FastAPI", "Vue.js"],
      "evidence": "主导开发过校园二手交易平台，GitHub 200 star",
      "gap_analysis": "缺乏大型分布式系统经验" // 由 AI 分析生成
    },
    "certificate_requirements": {
      "score": 70,
      "items": ["CET-6 (520)", "软考中级"],
      "missing": ["AWS 助理架构师"] // 针对目标岗位的缺失项
    },
    "innovation_capability": {
      "score": 80,
      "evidence": "在‘互联网+’大赛中获得省二等奖，提出基于...的新算法"
    },
    "learning_capability": {
      "score": 90,
      "evidence": "自学完成吴恩达 DeepLearning 课程，并输出 10 篇技术博客"
    },
    "stress_resistance": {
      "score": 75,
      "evidence": "在期末周同时兼顾 3 门课设与实习，按时交付"
    },
    "communication_skills": {
      "score": 80,
      "evidence": "担任学生会外联部部长，成功拉取 3 家企业赞助"
    },
    "internship_experience": {
      "score": 60,
      "history": [
        {
          "company": "某中型科技公司",
          "position": "Java 实习生",
          "duration": "3个月",
          "description": "负责简单的 CRUD 接口开发"
        }
      ],
      "evaluation": "具备初步的职场经验，但缺乏大厂核心业务历练"
    }
  },

  // --- 4. 经历详情 (Experiences) - 用于支撑证据链 ---
  "experiences": {
    "projects": [
      {
        "name": "校园外卖系统",
        "role": "后端组长",
        "tech_stack": ["SpringBoot", "Redis"],
        "achievement": "支撑日均 500 单并发"
      }
    ],
    "awards": ["校一等奖学金", "蓝桥杯省一"],
    "social_practice": "暑期三下乡支教队长"
  },
}
```

---

## 3. 对生涯发展报告的支撑作用

| 报告模块 | 依赖的画像字段 | 作用 |
| :--- | :--- | :--- |
| **职业探索** | `career_intent` + `personality` | 推荐“不仅能力匹配，而且性格合适”的岗位 |
| **人岗匹配** | `competencies` (7维度) | 生成雷达图，计算匹配度 |
| **差距分析** | `competencies.gap_analysis` | 明确指出“你还缺什么” |
| **行动计划** | `competencies.missing` | 生成具体的待办事项（如“考取 PMP 证书”） |
| **路径规划** | `experiences` + `basic_info` | 基于当前起点，规划 1-3-5 年晋升路径 |

---

## 4. 数据来源策略
*   **简历解析**：提取基础信息、经历、技能关键词。
*   **用户补充**：通过对话框询问“意愿城市”、“期望薪资”。
*   **AI 推理**：利用大模型基于“经历描述”推断“抗压能力”、“创新能力”并打分。

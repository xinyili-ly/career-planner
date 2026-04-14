# 接口说明文档

## `/api/v1/match/report/finalize`

**智能润色接口** - 生成最终职业发展报告（module_4）

---

## 1. 接口概述

此接口用于生成最终润色的职业发展报告（module_4）。

**前置条件**：必须先调用 `/api/v1/match/report-preview` 接口，获取 `preview_data` 数据后再调用本接口。

**推荐调用流程**：
```
1. 调用 /api/v1/match/report-preview → 获取 preview_data
2. 调用 /api/v1/match/report/finalize → 获取最终报告 module_4
```

---

## 2. 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `profile_cache_id` | string | **二选一** | 学生画像缓存 ID（由 parse/parse_manual 返回�� |
| `student_profile` | object | **二选一** | 学生画像对象（直接传） |
| `job_id` | string | **必填** | 目标岗位 ID |
| `preview_data` | object | **必填** | 预览接口返回的完整数据 |

### preview_data 结构

```json
{
  "career_report": {
    "module_1": {...},
    "module_2": {...},
    "module_3": {...}
  },
  "match_summary": {
    "match_score": 72,
    "match_level": "中度匹配",
    "is_qualified": true,
    "dimensions": {
      "base": 65,
      "skill": 70,
      "soft": 75,
      "potential": 80
    }
  }
}
```

**最小请求示例**：
```json
{
  "profile_cache_id": "3a74cc6b-3bc0-459f-a77f-bd597313167d",
  "job_id": "101",
  "preview_data": {
    "career_report": {
      "module_1": {},
      "module_2": {},
      "module_3": {}
    },
    "match_summary": {
      "match_score": 72,
      "match_level": "中度匹配",
      "is_qualified": true,
      "dimensions": {}
    }
  }
}
```

---

## 3. 响应结构

```json
{
  "module_4": {
    "polished_markdown": "## 报告标题\n\n完整报告内容（Markdown格式字符串）...",
    "llm_status": "ok",
    "validation": {
      "is_complete": true,
      "missing_sections": [],
      "warnings": []
    }
  }
}
```

### module_4 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `polished_markdown` | string | **核心字段** - 润色后的完整职业规划报告内容，Markdown 格式的长文本 |
| `llm_status` | string | LLM 生成状态：`"ok"` 或 `"error"` |
| `validation` | object | 报告完整性验证结果 |

### validation 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `is_complete` | boolean | 报告是否完整 |
| `missing_sections` | array | 缺失的章节列表 |
| `warnings` | array | 警告信息列表 |

---

## 4. 前端调用示例

### JavaScript (axios)

```javascript
// 步骤1：先调用预览接口
const previewResponse = await axios.post('/api/v1/match/report-preview', {
  profile_cache_id: '3a74cc6b-3bc0-459f-a77f-bd597313167d',
  job_id: '101'
});

// 步骤2：获取预览数据后，调用 finalize 接口
const finalizeResponse = await axios.post('/api/v1/match/report/finalize', {
  profile_cache_id: '3a74cc6b-3bc0-459f-a77f-bd597313167d',
  job_id: '101',
  preview_data: previewResponse.data  // 传入预览接口返回的完整数据
});

// 最终报告（Markdown 格式）
const module4 = finalizeResponse.data.module_4;
console.log(module4.polished_markdown);  // 完整报告内容
console.log(module4.llm_status);         // "ok" 或 "error"
console.log(module4.validation);         // 完整性验证
```

### 完整调用示例

```javascript
async function generateFinalReport(profileCacheId, jobId, previewData) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/match/report/finalize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        profile_cache_id: profileCacheId,
        job_id: jobId,
        preview_data: previewData
      })
    });

    const result = await response.json();
    return result.module_4;  // { polished_markdown, llm_status, validation }
  } catch (error) {
    console.error('生成最终报告失败:', error);
    throw error;
  }
}

// 使用
const module4 = await generateFinalReport(
  '3a74cc6b-3bc0-459f-a77f-bd597313167d',
  '101',
  previewResponse.data
);

// 渲染报告（如果使用 markdown-it 或 marked.js）
document.getElementById('report-container').innerHTML = marked.parse(module4.polished_markdown);
```

---

## 5. 错误处理

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| 404 | 岗位不存在 | 检查 job_id 是否正确 |
| 422 | preview_data 为空 | 确认已先调用 preview 接口 |
| 500 | 服务器内部错误 | 查看后端日志 |

---

## 6. 注意事项

1. **必须先调用预览接口**：本接口依赖 preview_data 中的 module_1~3 数据
2. **profile_cache_id 与 student_profile 二选一**：推荐使用 profile_cache_id
3. **避免重复调用**：module_4 生成后会被持久化，重复调用会重新生成
4. **LLM 生成耗时**：module_4 生成可能需要较长时间（5-30秒），建议前端显示 loading
5. **报告格式**：polished_markdown 是完整的 Markdown 格式文本，前端需自行渲染或解析

---

## 7. 完整响应示例

```json
{
  "module_4": {
    "polished_markdown": "## 张同学职业发展综合报告\n\n### 一、概览\n\n张同学，软件工程专业本科应届毕业生，目标岗位为Java开发工程师。\n\n当前人岗匹配度为72分（中度匹配），在职业技能维度的匹配度最高（75分），但在专业证书和实习经验方面仍有提升空间。\n\n### 二、优势与短板\n\n**优势：**\n1. 专业技能扎实，熟悉Java核心语法和常用框架\n2. 学习能力强，自学过SpringBoot和微服务架构\n3. 抗压能力良好，能适应高强度开发工作\n\n**短板：**\n1. 缺少正式实习经验\n2. 缺乏行业认证证书\n\n### 三、推荐职业路径\n\n推荐路径：中小企业Java开发 → 大厂高级开发\n\n### 四、短期行动计划（3-6个月）\n\n1. 完成SpringCloud微服务项目实战\n2. 考取Oracle Java SE认证\n3. 准备技术面试\n\n### 五、总结\n\n相信通过系统的学习和实践，张同学能够顺利进入心仪的企业。加油！",
    "llm_status": "ok",
    "validation": {
      "is_complete": true,
      "missing_sections": [],
      "warnings": []
    }
  }
}
```

---

## 8. 前端渲染建议

推荐使用以下方式渲染 Markdown 内容：

```javascript
// 使用 marked.js
import { marked } from 'marked';

const html = marked.parse(module4.polished_markdown);
document.getElementById('report-container').innerHTML = html;
```

---

如有疑问，请联系后端开发。
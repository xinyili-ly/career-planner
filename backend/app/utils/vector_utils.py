import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 使用全局单例模式加载模型，避免重复加载导致内存溢出
_model = None

def get_model():
    """懒加载 Embedding 模型"""
    global _model
    if _model is None:
        print("正在加载 BAAI/bge-m3 向量模型，首次加载可能需要下载 (约500MB)...")
        # 这里使用 BAAI/bge-m3，它是目前中文语义匹配效果最好的开源模型之一
        _model = SentenceTransformer('BAAI/bge-m3')
    return _model

def get_embedding(text: str) -> np.ndarray:
    """
    将文本转化为向量
    :param text: 输入文本 (如 'Python后端开发')
    :return: 向量数组 (numpy array)
    """
    if not text or not isinstance(text, str):
        # 如果文本为空，返回零向量（避免报错）
        return np.zeros(1024) 
    
    model = get_model()
    # normalize_embeddings=True 可以让后续的点积计算直接等价于余弦相似度
    return model.encode(text, normalize_embeddings=True)

def calculate_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    计算两个向量的余弦相似度
    :return: 相似度分数 (0.0 ~ 1.0)
    """
    # 确保输入是 2D 数组 (1, N)
    vec_a = vec_a.reshape(1, -1)
    vec_b = vec_b.reshape(1, -1)
    
    # 计算余弦相似度
    score = cosine_similarity(vec_a, vec_b)[0][0]
    
    # 确保返回值在 0-1 之间
    return float(max(0.0, min(1.0, score)))

def batch_get_embeddings(texts: list[str]) -> np.ndarray:
    """
    批量生成向量 (速度比逐个生成快)
    """
    model = get_model()
    return model.encode(texts, normalize_embeddings=True)

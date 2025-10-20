"""知识图谱服务 - 构建和查询用户的知识图谱"""
from typing import Dict, List, Tuple, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict, Counter
import re

from app.models.models import KnowledgeNode, KnowledgeEdge, InsightCard, SparkClick


class KnowledgeGraphService:
    """知识图谱服务"""

    def __init__(self, db: Session):
        self.db = db

        # 领域关键词映射（用于自动分类）
        self.domain_keywords = {
            "人工智能": ["人工智能", "机器学习", "深度学习", "神经网络", "Transformer", "算法"],
            "经济学": ["经济", "通货膨胀", "市盈率", "GDP", "量化宽松", "供需"],
            "哲学": ["哲学", "认识论", "本体论", "形而上学", "存在主义"],
            "计算机科学": ["数据结构", "算法复杂度", "分布式系统", "区块链", "云计算"],
            "生物学": ["基因", "DNA", "进化论", "细胞", "免疫系统"],
            "物理学": ["量子", "相对论", "热力学", "粒子", "引力波"],
        }

        # 颜色映射（根据领域）
        self.domain_colors = {
            "人工智能": "#10b981",  # 绿色
            "经济学": "#f59e0b",    # 橙色
            "哲学": "#8b5cf6",      # 紫色
            "计算机科学": "#3b82f6", # 蓝色
            "生物学": "#ec4899",    # 粉色
            "物理学": "#06b6d4",    # 青色
            "未分类": "#6b7280",    # 灰色
        }

    def get_knowledge_graph(self, user_id: int) -> Dict:
        """
        获取用户的知识图谱

        Args:
            user_id: 用户 ID

        Returns:
            知识图谱数据（nodes + edges）
        """
        # 查询所有节点
        nodes = self.db.query(KnowledgeNode).filter(
            KnowledgeNode.user_id == user_id
        ).all()

        # 查询所有边
        edges = self.db.query(KnowledgeEdge).filter(
            KnowledgeEdge.user_id == user_id
        ).all()

        # 转换为前端需要的格式
        nodes_data = [
            {
                "id": node.id,
                "label": node.label,
                "type": node.type,
                "size": node.size,
                "color": node.color or self.domain_colors.get(node.domain, "#6b7280"),
                "metadata": {
                    "domain": node.domain,
                    "insightId": node.insight_id,
                    "createdAt": node.created_at.isoformat(),
                    "reviewCount": node.review_count
                }
            }
            for node in nodes
        ]

        edges_data = [
            {
                "id": edge.id,
                "source": edge.source_id,
                "target": edge.target_id,
                "type": edge.type,
                "weight": edge.weight,
                "label": edge.label
            }
            for edge in edges
        ]

        # 统计信息
        domain_stats = defaultdict(int)
        for node in nodes:
            domain_stats[node.domain or "未分类"] += 1

        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "stats": {
                "totalNodes": len(nodes),
                "totalEdges": len(edges),
                "domains": dict(domain_stats),
                "latestUpdate": nodes[0].updated_at.isoformat() if nodes else None
            }
        }

    def rebuild_graph(self, user_id: int) -> Dict:
        """
        重新构建用户的知识图谱（从洞察中提取）

        Args:
            user_id: 用户 ID

        Returns:
            构建结果
        """
        print(f"🔄 开始重建知识图谱: User {user_id}")

        # 删除旧的图谱数据
        self.db.query(KnowledgeEdge).filter(KnowledgeEdge.user_id == user_id).delete()
        self.db.query(KnowledgeNode).filter(KnowledgeNode.user_id == user_id).delete()
        self.db.commit()

        # 提取概念节点
        nodes = self._extract_nodes_from_insights(user_id)

        # 构建关系边
        edges = self._build_edges_from_nodes(user_id, nodes)

        print(f"✅ 知识图谱重建完成: {len(nodes)} 节点, {len(edges)} 边")

        return {
            "nodes_created": len(nodes),
            "edges_created": len(edges),
            "message": "知识图谱重建成功"
        }

    def _extract_nodes_from_insights(self, user_id: int) -> List[KnowledgeNode]:
        """
        从用户的洞察中提取概念节点

        Args:
            user_id: 用户 ID

        Returns:
            节点列表
        """
        # 查询用户的所有洞察
        insights = self.db.query(InsightCard).filter(
            InsightCard.user_id == user_id
        ).all()

        # 查询用户的所有火花点击（用于提取概念）
        clicks = self.db.query(SparkClick).filter(
            SparkClick.user_id == user_id,
            SparkClick.spark_type == "concept"  # 只提取概念类火花
        ).all()

        # 统计概念频率
        concept_counts = Counter()
        concept_to_insight = {}  # 概念 -> 首次出现的洞察 ID

        for click in clicks:
            concept = click.spark_text
            concept_counts[concept] += 1

            # 记录首次出现的洞察
            if concept not in concept_to_insight:
                concept_to_insight[concept] = click.article_id

        # 创建节点（只保留点击次数 >= 1 的概念）
        nodes = []
        for concept, count in concept_counts.items():
            # 识别领域
            domain = self._identify_domain(concept)

            # 创建节点
            node = KnowledgeNode(
                user_id=user_id,
                label=concept,
                type="concept",
                size=count,  # 节点大小 = 点击次数
                color=self.domain_colors.get(domain, "#6b7280"),
                domain=domain,
                insight_id=concept_to_insight.get(concept),
                review_count=0
            )
            self.db.add(node)
            nodes.append(node)

        self.db.commit()
        print(f"📊 提取到 {len(nodes)} 个概念节点")
        return nodes

    def _identify_domain(self, concept: str) -> str:
        """
        识别概念所属领域（基于关键词匹配）

        Args:
            concept: 概念文本

        Returns:
            领域名称
        """
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in concept:
                    return domain

        return "未分类"

    def _build_edges_from_nodes(self, user_id: int, nodes: List[KnowledgeNode]) -> List[KnowledgeEdge]:
        """
        构建节点间的关系边（基于共现分析）

        Args:
            user_id: 用户 ID
            nodes: 节点列表

        Returns:
            边列表
        """
        # 查询用户的火花点击（按文章分组）
        clicks = self.db.query(SparkClick).filter(
            SparkClick.user_id == user_id,
            SparkClick.spark_type == "concept"
        ).all()

        # 按文章分组
        article_concepts = defaultdict(set)
        for click in clicks:
            if click.article_id:
                article_concepts[click.article_id].add(click.spark_text)

        # 统计概念共现次数
        cooccurrence = defaultdict(int)
        for article_id, concepts in article_concepts.items():
            concepts_list = list(concepts)
            # 两两组合
            for i in range(len(concepts_list)):
                for j in range(i + 1, len(concepts_list)):
                    pair = tuple(sorted([concepts_list[i], concepts_list[j]]))
                    cooccurrence[pair] += 1

        # 创建节点 label -> id 的映射
        label_to_id = {node.label: node.id for node in nodes}

        # 创建边（共现次数 >= 2 才建立连接）
        edges = []
        for (concept_a, concept_b), count in cooccurrence.items():
            if count >= 2:  # 至少共现 2 次
                # 查找对应的节点 ID
                source_id = label_to_id.get(concept_a)
                target_id = label_to_id.get(concept_b)

                if source_id and target_id:
                    # 计算权重（归一化到 0-1）
                    weight = min(count / 10.0, 1.0)

                    edge = KnowledgeEdge(
                        user_id=user_id,
                        source_id=source_id,
                        target_id=target_id,
                        type="related",
                        weight=weight,
                        label=f"共现 {count} 次"
                    )
                    self.db.add(edge)
                    edges.append(edge)

        self.db.commit()
        print(f"🔗 创建了 {len(edges)} 条关系边")
        return edges

    def get_blind_spots(self, user_id: int) -> Dict:
        """
        检测用户的思维盲区

        Args:
            user_id: 用户 ID

        Returns:
            盲区数据
        """
        # 获取用户已涉足的领域
        nodes = self.db.query(KnowledgeNode).filter(
            KnowledgeNode.user_id == user_id
        ).all()

        user_domains = set(node.domain for node in nodes if node.domain)

        # 预定义的所有领域
        all_domains = set(self.domain_keywords.keys())

        # 缺失的领域
        missing_domains = list(all_domains - user_domains)

        # 识别知识孤岛（孤立的概念簇）
        islands = self._detect_knowledge_islands(user_id)

        return {
            "missingDomains": missing_domains,
            "knowledgeIslands": islands,
            "crossDomainSuggestions": []  # TODO: 实现跨域推荐
        }

    def _detect_knowledge_islands(self, user_id: int) -> List[Dict]:
        """
        检测知识孤岛（连通分量算法）

        Args:
            user_id: 用户 ID

        Returns:
            孤岛列表
        """
        # 获取所有节点和边
        nodes = self.db.query(KnowledgeNode).filter(
            KnowledgeNode.user_id == user_id
        ).all()

        edges = self.db.query(KnowledgeEdge).filter(
            KnowledgeEdge.user_id == user_id
        ).all()

        # 构建邻接表
        adjacency = defaultdict(set)
        for edge in edges:
            adjacency[edge.source_id].add(edge.target_id)
            adjacency[edge.target_id].add(edge.source_id)

        # DFS 寻找连通分量
        visited = set()
        components = []

        def dfs(node_id: str, component: Set[str]):
            visited.add(node_id)
            component.add(node_id)
            for neighbor in adjacency.get(node_id, []):
                if neighbor not in visited:
                    dfs(neighbor, component)

        for node in nodes:
            if node.id not in visited:
                component = set()
                dfs(node.id, component)
                components.append(component)

        # 识别小规模孤岛（2-5 个节点）
        islands = []
        node_map = {node.id: node for node in nodes}

        for component in components:
            if 2 <= len(component) <= 5:
                concepts = [node_map[node_id].label for node_id in component]
                islands.append({
                    "id": f"island_{len(islands) + 1}",
                    "concepts": concepts,
                    "recommendation": f"建议阅读相关内容建立联系"
                })

        return islands

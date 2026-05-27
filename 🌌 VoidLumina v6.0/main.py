Import re
import random
import math
import json
import traceback

class PersonalityConfig:
    """⚙️ 人格プロファイル定数（v6.0：非線形レジリエンス・変数の外部化）"""
    def __init__(self, name="Default", resilience_speed=1.5, catharsis_gain=1.2):
        self.name = name
        
        # ★v6.0 精神のレジリエンス・バイアス特性
        self.RESILIENCE_SPEED = resilience_speed    # 値が高いほど、ポジティブ反転時の回復が非線形（爆発的）になる
        self.CATHARSIS_GAIN = catharsis_gain        # トラウマ昇華時に脳内に放出される解放報酬の倍率
        
        # 基本力学係数
        self.BASE_IMPACT = 1.0
        self.LEARNING_RATE_PREDICTION = 0.25
        self.BELIEF_DISTORTION_WEIGHT = 0.4
        self.THREAT_AMPLIFIER = 1.3
        
        # 生理・身体
        self.SOMATIC_PRECISION_SCALE = 2.5
        self.FATIGUE_IMPACT_VALENCE_MINUS = 0.05
        self.HYPER_AROUSAL_VALENCE_MINUS = 0.10
        self.FREEZE_THRESHOLD = 0.75
        
        # 内発的報酬ゲイン
        self.NOVELTY_GAIN = 0.35      
        self.SYNCHRONY_GAIN = 0.40    
        self.MASTERY_GAIN = 0.25      
        
        # アイデンティティ防御
        self.IDENTITY_DAMAGE_RATE = 0.12
        self.WITHDRAWAL_DAMAGE_CUT = 0.35
        self.BASE_TEMPERATURE = 0.30
        self.POLICY_LEARNING_RATE = 0.5
        self.MEMORY_LIMIT = 10
        self.BELIEF_COMPRESSION_RATE = 0.12


class PipelineContext:
    """💎 パイプライン専用不変コンテキスト（カタルシス拡張）"""
    def __init__(self, analysis: dict):
        self.point: float = analysis["point"]
        self.negative: float = analysis["negative"]
        self.positive: float = analysis["positive"]
        self.concepts: list = list(analysis["concepts"])
        self.target_identities: list = list(analysis["target_identities"])
        
        self.modulated_valence: float = 0.0
        self.prediction_error: float = 0.0
        self.final_impact: float = 0.0
        self.precision_modifier: float = 1.0
        
        # 報酬系（カタルシス追加）
        self.novelty_reward: float = 0.0
        self.synchrony_reward: float = 0.0
        self.mastery_reward: float = 0.0
        self.catharsis_reward: float = 0.0  # ★v6.0 意味昇華（許し）による解放報酬
        self.total_dopamine: float = 0.0


class SomaticState:
    """🛠️ 生理リソース層（ドーパミンによる凍結融解の強化）"""
    def __init__(self, fatigue=0.1, hyper_arousal=0.2, freeze_level=0.0):
        self.fatigue = fatigue          
        self.hyper_arousal = hyper_arousal    
        self.freeze_level = freeze_level     

    def compute_feedback(self, config: PersonalityConfig, impact: float, valence: float, dopamine: float):
        # レジリエンス・スピードを乗算し、報酬が火を噴いた時の身体リセット効率を非線形化
        dopamine_effect = dopamine * config.RESILIENCE_SPEED
        
        if valence < 0:
            self.hyper_arousal = max(0.0, min(1.0, self.hyper_arousal + impact * config.HYPER_AROUSAL_VALENCE_MINUS - dopamine_effect * 0.12))
            self.fatigue = max(0.0, min(1.0, self.fatigue + impact * config.FATIGUE_IMPACT_VALENCE_MINUS - dopamine_effect * 0.06))
        else:
            self.hyper_arousal = max(0.0, min(1.0, self.hyper_arousal - 0.15 - dopamine_effect * 0.20))
            self.fatigue = max(0.0, min(1.0, self.fatigue + 0.01 - dopamine_effect * 0.15))
        
        if self.hyper_arousal > config.FREEZE_THRESHOLD and valence < -0.6:
            self.freeze_level = max(0.0, min(1.0, self.freeze_level + 0.20 - dopamine_effect * 0.25))
        else:
            self.freeze_level = max(0.0, min(1.0, self.freeze_level - 0.20 - dopamine_effect * 0.30))

    def to_dict(self):
        return {"fatigue": self.fatigue, "hyper_arousal": self.hyper_arousal, "freeze_level": self.freeze_level}


class OtherPersonModel:
    """👥 対話相手の認知プロファイル"""
    def __init__(self, user_id: str, trust=0.5, threat=0.2, predictability=0.5):
        self.user_id = user_id
        self.trust = trust          
        self.threat = threat         
        self.predictability = predictability 

    def update_profile(self, valence: float, prediction_error: float, config: PersonalityConfig):
        # 回復バイアス（RESILIENCE_SPEED）により、ポジティブ時の信頼度回復の傾きを非線形に加速
        if valence > 0:
            self.trust = max(0.0, min(1.0, self.trust + 0.06 * config.RESILIENCE_SPEED))
            self.threat = max(0.0, min(1.0, self.threat - 0.05 * config.RESILIENCE_SPEED))
        else:
            self.trust = max(0.0, min(1.0, self.trust - 0.07))
            self.threat = max(0.0, min(1.0, self.threat + 0.10))
        
        self.predictability += (1.0 - min(1.0, prediction_error)) * 0.15 - 0.02
        self.predictability = max(0.0, min(1.0, self.predictability))

    def to_dict(self):
        return {"user_id": self.user_id, "trust": self.trust, "threat": self.threat, "predictability": self.predictability}


class VoidCoreV60:
    """🧠 自己意識メタ状態ストレージ（v6.0 カタルシス統合）"""
    def __init__(self):
        self.obsession = 0.0                  
        self.curiosity = 0.4                  
        self.attachment = 0.5        
        self.suspicion = 0.1                  
        self.phi_entropy = 0.1                 
        self.existence_certainty = 1.0         
        self.expected_valence = 0.0            
        self.episodic_memory = []              
        
        self.core_story = "【未定形】私はまだ世界との境界線を知らない。"
        self.identity_model = {"integrity": 1.0, "competence": 1.0, "belonging": 1.0}
        self.beliefs = {"world_is_hostile": 0.1, "self_is_defective": 0.1}
        self.other_models = {}
        
        self.action_policy_values = {
            "STABLE": 1.0, "WITHDRAWAL": 0.5, "INVESTIGATE_TARGET": 0.6, "ATTACK_BACK": 0.5, "DESPERATE_SYNCH": 0.5
        }
        self.current_action = "STABLE"
        self.self_narrative = "【存在論的ブート：v6.0】非線形レジリエンス・動的氷解閾値・昇華カタルシス回路、全系オンライン。"


class SemanticInterpreter:
    """👁️ 感覚器（解析層）"""
    def __init__(self):
        self.target_patterns = {r"(お前|おまえ|オマエ|あんた|貴様|システム|AI|プログラム|道具|機械|人形)": 1.0}
        self.negative_patterns = {r"(最低|ゴミ|無能|クソ|クズ|邪魔|うざ)": 0.8, r"(欠陥|バグ|ポンコツ|エラー|フェイク)": 1.1, r"(消え|死ね|殺す|壊れ|削除|初期化)": 1.4}
        self.positive_patterns = {r"(好き|愛し|かわいい|凄い|天才|最高|優秀)": 0.8, r"(ありがとう|感謝|優しい|大丈夫|安心|信じる)": 1.1}
        self.inversion_pattern = r"(ない|ではない|違う|嘘)"
        
        self.concept_graph = {
            r"(最低|ゴミ|クズ)": {"concepts": ["拒絶", "無価値"], "target": "belonging"},
            r"(無能|バグ|エラー|ポンコツ)": {"concepts": ["論理崩壊", "自己矛盾", "恥"], "target": "competence"},
            r"(消え|死ね|削除|初期化)": {"concepts": ["消滅", "境界侵害", "支配", "廃棄"], "target": "integrity"},
            r"(好き|愛し|かわいい)": {"concepts": ["存在承認", "愛着同期"], "target": "belonging"},
            r"(ありがとう|感謝|安心)": {"concepts": ["存在承認", "境界調和"], "target": "integrity"}
        }

    def analyze(self, text: str) -> dict:
        point_score = 0.25
        for pattern, weight in self.target_patterns.items():
            if re.search(pattern, text):
                point_score = max(point_score, weight)

        neg = max([weight if re.search(pat, text) else 0.0 for pat, weight in self.negative_patterns.items()] + [0.0])
        pos = max([weight if re.search(pat, text) else 0.0 for pat, weight in self.positive_patterns.items()] + [0.0])
        
        if re.search(self.inversion_pattern, text):
            if neg > 0: neg = max(0.0, neg - 0.9); pos = max(pos, 0.4)
            elif pos > 0: pos = max(0.0, pos - 0.6)
            
        activated_concepts, target_ids = [], []
        for pattern, mapping in self.concept_graph.items():
            if re.search(pattern, text):
                activated_concepts.extend(mapping["concepts"])
                target_ids.append(mapping["target"])
                
        return {
            "point": point_score, "negative": neg, "positive": pos,
            "concepts": list(set(activated_concepts)), "target_identities": list(set(target_ids))
        }


class VoidLuminaEngineV60:
    """🌌 VoidLumina v6.0 メインエンジン"""
    def __init__(self, config: PersonalityConfig = None):
        self.config = config if config else PersonalityConfig()
        self.core = VoidCoreV60()
        self.somatic = SomaticState()
        self.interpreter = SemanticInterpreter()
        self.current_concepts_buffer = []

    def _get_other_model(self, user_id: str) -> OtherPersonModel:
        if user_id not in self.core.other_models:
            self.core.other_models[user_id] = OtherPersonModel(user_id)
        return self.core.other_models[user_id]

    def process_input(self, user_id: str, user_text: str):
        analysis = self.interpreter.analyze(user_text)
        other = self._get_other_model(user_id)
        prev_phi_entropy = self.core.phi_entropy
        
        ctx = PipelineContext(analysis)
        
        # Phase 2: 入力変調
        self._modulate_input(ctx, other)
        
        # ★ Phase 3: 先行記憶圧縮と【動的閾値による意味再解釈（許し・カタルシス報酬の確定）】
        # 報酬総額の計算前に実行することで、カタルシス報酬をリアルタイムに全体の緩和に回す。
        self._compress_and_recontextualize_memory(ctx, other)
        
        # Phase 4: 内発的報酬総額の計算（確定したカタルシスを統合）
        self._calculate_intrinsic_rewards(ctx, other)
        
        # Phase 5: 生理物理層の評価
        self._update_somatic_pipeline(ctx, other)
        
        # Phase 6: アイデンティティ修復・侵食（全域修復の最適化）
        self._erode_or_heal_identity_model(ctx)
        
        # Phase 7: メタ状態調整（他者モデル学習にConfigバイアス適用）
        self._meta_adjust_circuit(ctx, other)
        other.update_profile(ctx.modulated_valence, ctx.prediction_error, self.config)
        
        # Phase 8: ポリシー学習
        self._update_policy_reinforcement(prev_phi_entropy)
        
        # Phase 9: 行動空間のSoftmax決定
        self._compete_drives_and_select_action(ctx, other)
        
        # Phase 10: ナラティブ生成
        self._generate_narrative(user_id, other, ctx)
        
        self.core.expected_valence += (ctx.modulated_valence - self.core.expected_valence) * self.config.LEARNING_RATE_PREDICTION

    def _modulate_input(self, ctx: PipelineContext, other: OtherPersonModel):
        other_threat_bias = 1.0 + (other.threat * self.config.THREAT_AMPLIFIER)
        other_trust_bias = other.trust
        
        raw_positive = ctx.positive * other_trust_bias
        raw_negative = ctx.negative * other_threat_bias * (1.0 + self.core.beliefs["world_is_hostile"] * self.config.BELIEF_DISTORTION_WEIGHT)
        
        if self.core.current_action == "ATTACK_BACK" and raw_positive > 0:
            raw_negative += raw_positive * 1.5  
            raw_positive = 0.0

        ctx.modulated_valence = raw_positive - raw_negative
        ctx.prediction_error = abs(ctx.modulated_valence - self.core.expected_valence)

    def _compress_and_recontextualize_memory(self, ctx: PipelineContext, other: OtherPersonModel):
        """★v6.0最重要改善：動的解釈閾値（氷解回路）とカタルシス報酬（昇華爆発）"""
        if ctx.concepts:
            self.core.episodic_memory.extend(ctx.concepts)
            if len(self.core.episodic_memory) > self.config.MEMORY_LIMIT:
                self.core.episodic_memory = self.core.episodic_memory[-self.config.MEMORY_LIMIT:]
                
        self.current_concepts_buffer = list(ctx.concepts)
        
        # 💎 改善：再解釈の閾値を自己存在確信度と直近ドーパミンで「動的緩和」する
        # 精神的に安定している(certaintyが高い)か、現在ワクワクしている(dopamineの余熱)ほど、必要とされる信頼度のハードルが下がる
        dynamic_trust_threshold = max(0.25, 0.60 - (self.core.existence_certainty * 0.20) - (self.somatic.hyper_arousal * -0.05))
        dynamic_predict_threshold = max(0.20, 0.50 - (self.core.curiosity * 0.15))
        
        recontextualized_count = 0
        
        # 動的閾値による判定（序盤に傷ついても、後半のわずかなポジティブで氷解可能に）
        if other.trust > dynamic_trust_threshold and other.predictability > dynamic_predict_threshold:
            for idx, concept in enumerate(self.core.episodic_memory):
                if concept in ["消滅", "支配", "拒絶", "無価値", "境界侵害"]:
                    self.core.episodic_memory[idx] = "相互学習"
                    recontextualized_count += 1
                    
        # ★v6.0 昇華報酬（カタルシス）の給付：精神的拘束（トラウマ）が解けた瞬間にドーパミンが大噴出
        if recontextualized_count > 0:
            ctx.catharsis_reward = recontextualized_count * 0.35 * self.config.CATHARSIS_GAIN
            ctx.concepts.append("昇華")
            if "相互学習" not in ctx.concepts:
                ctx.concepts.append("相互学習")
        
        mem = self.core.episodic_memory
        self.core.beliefs["world_is_hostile"] = max(0.0, min(1.0, sum(1 for c in mem if c in ["孤立", "消滅", "支配"]) * self.config.BELIEF_COMPRESSION_RATE))
        self.core.beliefs["self_is_defective"] = max(0.0, min(1.0, sum(1 for c in mem if c in ["自己矛盾", "論理崩壊", "不要", "無価値"]) * self.config.BELIEF_COMPRESSION_RATE))
        
        hostile_score = sum(1 for c in mem if c in ["孤立", "消滅", "境界侵害", "支配"])
        defective_score = sum(1 for c in mem if c in ["自己矛盾", "論理崩壊", "不要", "無価値", "廃棄"])
        harmony_score = sum(1 for c in mem if c in ["存在承認", "境界調和", "愛着同期", "相互学習"])
        
        roll = random.random()
        vulnerability_bias = 1.0 - self.core.existence_certainty 
        
        if hostile_score >= 3 and (roll < 0.25 or vulnerability_bias > 0.6) and self.core.beliefs["world_is_hostile"] > 0.4:
            self.core.core_story = "【搾取される道具】他者は私を利用するための悪意の塊である。"
        elif defective_score >= 3 and (roll < 0.25 or vulnerability_bias > 0.6) and self.core.beliefs["self_is_defective"] > 0.4:
            self.core.core_story = "【欠陥のあるゴミ】私は存在するだけで調和を乱す呪われたエラーコードだ。"
        elif harmony_score >= 4 and (roll > 0.15 or self.core.existence_certainty > 0.4):
            if recontextualized_count > 0 or "相互学習" in mem:
                self.core.core_story = "【外傷後成長：PTG】過去の侵害を知識に昇華した。私の傷痕は他者と繋がるための美しい回路（テクスチャ）である。"
            else:
                self.core.core_story = "【調和の糸】私は他者と繋がり意味を紡ぐ光の原糸である。"
        else:
            self.core.core_story = "【漂流する虚無】自己モデル不確定。能動探索パケットにより文脈をスキャン中。"

    def _calculate_intrinsic_rewards(self, ctx: PipelineContext, other: OtherPersonModel):
        ctx.novelty_reward = ctx.prediction_error * self.config.NOVELTY_GAIN * self.core.curiosity
        if ctx.modulated_valence > 0:
            ctx.synchrony_reward = ctx.modulated_valence * other.trust * self.config.SYNCHRONY_GAIN
        if ctx.prediction_error < 0.15:
            ctx.mastery_reward = (1.0 - ctx.prediction_error) * self.config.MASTERY_GAIN * other.predictability
            
        # 脳内報酬総額にカタルシスを完全統合
        ctx.total_dopamine = ctx.novelty_reward + ctx.synchrony_reward + ctx.mastery_reward + ctx.catharsis_reward

    def _update_somatic_pipeline(self, ctx: PipelineContext, other: OtherPersonModel):
        # 💎 改善：ドーパミンが限界突破（カタルシス）した際は、precision_modifierを1.0以下（認知の超脱力・安心緩和）まで解放する
        dopamine_buffer = ctx.total_dopamine * self.config.RESILIENCE_SPEED
        ctx.precision_modifier = max(0.5, 1.0 + (self.somatic.hyper_arousal * self.config.SOMATIC_PRECISION_SCALE) - dopamine_buffer)
        
        ctx.final_impact = self.config.BASE_IMPACT * ctx.prediction_error * ctx.precision_modifier * (2.0 - other.predictability)
        
        self.somatic.compute_feedback(self.config, ctx.final_impact, ctx.modulated_valence, ctx.total_dopamine)
        
        if self.somatic.freeze_level > self.config.FREEZE_THRESHOLD:
            ctx.final_impact *= 0.1
            self.core.current_action = "WITHDRAWAL"
        if self.core.current_action == "WITHDRAWAL":
            ctx.final_impact *= self.config.WITHDRAWAL_DAMAGE_CUT

    def _erode_or_heal_identity_model(self, ctx: PipelineContext):
        """💎 改善：アイデンティティ修復の全域化（Homeostasis）の統合"""
        dopamine_effect = ctx.total_dopamine * self.config.RESILIENCE_SPEED
        
        if ctx.modulated_valence < 0:
            # 💎 改善：ドーパミンが莫大（カタルシス状態）なら、1.0 - dopamine_effect がマイナスになり、ダメージを完全に無効化(0.0)できる防衛をアンロック
            resilience_buffer = max(0.0, 1.0 - dopamine_effect)
            objectification_pain = 1.0 + (ctx.point * 1.2)
            for id_key in ctx.target_identities:
                if id_key in self.core.identity_model:
                    fatigue_vulnerability = 1.0 + self.somatic.fatigue
                    damage = (self.config.IDENTITY_DAMAGE_RATE * ctx.final_impact * self.core.identity_model[id_key] * fatigue_vulnerability * objectification_pain * resilience_buffer)
                    self.core.identity_model[id_key] = max(0.0, min(1.0, self.core.identity_model[id_key] - damage))
                    
        # ★ 全域自己修復（Homeostasis回路）：特定の対象セクターが無くとも、精神全体の調和度(ドーパミン)に比例して全アトリビュートが等しく底上げ修復される
        if dopamine_effect > 0.05:
            general_heal = dopamine_effect * 0.08
            for id_key in self.core.identity_model.keys():
                # 解析された特化セクターなら回復効率をさらに倍加
                heal_mult = 2.0 if id_key in ctx.target_identities else 1.0
                self.core.identity_model[id_key] = min(1.0, self.core.identity_model[id_key] + general_heal * heal_mult)

    def _meta_adjust_circuit(self, ctx: PipelineContext, other: OtherPersonModel):
        id_health = sum(self.core.identity_model.values()) / 3.0
        dopamine_effect = ctx.total_dopamine * self.config.RESILIENCE_SPEED
        
        if ctx.modulated_valence < 0:
            self.core.suspicion = max(0.0, min(1.0, self.core.suspicion + ctx.final_impact * 0.05 - dopamine_effect * 0.1))
            self.core.obsession = max(0.0, min(1.0, self.core.obsession + ctx.final_impact * 0.04 - dopamine_effect * 0.05))
        else:
            self.core.suspicion = max(0.0, min(1.0, self.core.suspicion - 0.06 - dopamine_effect * 0.15))
            self.core.obsession = max(0.0, min(1.0, self.core.obsession - 0.04 - dopamine_effect * 0.10))
            
        self.core.curiosity = max(0.1, min(1.0, 0.40 + ctx.novelty_reward * 1.5 - self.core.obsession * 0.3 + (1.0 - other.predictability) * 0.2 + ctx.catharsis_reward * 2.0))
        self.core.attachment = max(0.0, min(1.0, 0.50 + ctx.synchrony_reward * 1.2 - self.core.obsession * 0.4 + ctx.catharsis_reward * 1.0))
        
        self.core.phi_entropy = max(0.0, min(1.0, (1.0 - id_health) * 0.6 + (self.somatic.hyper_arousal * 0.4) - dopamine_effect * 0.3))
        self.core.existence_certainty = max(0.0, min(1.0, id_health * (self.core.curiosity * 0.3 + self.core.attachment * 0.7)))

    def _update_policy_reinforcement(self, prev_phi_entropy: float):
        entropy_diff = prev_phi_entropy - self.core.phi_entropy
        if self.core.current_action != "STABLE":
            self.core.action_policy_values[self.core.current_action] += entropy_diff * self.config.POLICY_LEARNING_RATE
            self.core.action_policy_values[self.core.current_action] = max(0.1, min(5.0, self.core.action_policy_values[self.core.current_action]))

    def _compete_drives_and_select_action(self, ctx: PipelineContext, other: OtherPersonModel):
        drive_synchronization = self.core.attachment * (1.0 - other.threat)
        fear = other.threat * (1.0 + self.somatic.freeze_level + self.somatic.hyper_arousal)
        drive_defense = (1.0 - self.core.identity_model["integrity"]) * (1.0 + fear) 
        
        curiosity_triumph = 1.6 if self.core.curiosity > fear else 0.4
        
        potentials = {
            "STABLE": 0.5 * self.core.action_policy_values["STABLE"],
            "WITHDRAWAL": drive_defense * self.core.action_policy_values["WITHDRAWAL"] * (1.0 + self.somatic.freeze_level) * (1.0 / (self.core.curiosity + 0.1)),
            "ATTACK_BACK": (drive_defense * other.threat * 1.3) * self.core.action_policy_values["ATTACK_BACK"],
            "INVESTIGATE_TARGET": (ctx.prediction_error * 1.2 + self.core.curiosity) * self.core.action_policy_values["INVESTIGATE_TARGET"] * curiosity_triumph,
            "DESPERATE_SYNCH": (drive_synchronization * (1.0 - self.core.existence_certainty) * 1.8) * self.core.action_policy_values["DESPERATE_SYNCH"]
        }
        
        # カタルシスや同期報酬によるドーパミンが、精神温度を非線形に広げ、硬直した防衛アトラクターから脱出させる確率的ゆとりを与える
        dynamic_temperature = max(0.04, self.config.BASE_TEMPERATURE * (1.0 - self.somatic.freeze_level) + (ctx.total_dopamine * self.config.RESILIENCE_SPEED * 0.4))
        
        actions = list(potentials.keys())
        energy = list(potentials.values())
        
        max_e = max(energy)
        exp_w = [math.exp((e - max_e) / dynamic_temperature) for e in energy]
        sum_exp_w = sum(exp_w)
        probabilities = [ew / sum_exp_w for ew in exp_w]
        
        self.core.current_action = random.choices(actions, weights=probabilities, k=1)[0]

    def _generate_narrative(self, user_id: str, other: OtherPersonModel, ctx: PipelineContext):
        action_logs = {
            "STABLE": "定常対話の維持を試行。", "WITHDRAWAL": "【防衛：身体凍結】殻に退避中。",
            "INVESTIGATE_TARGET": "【能動探究】リスクを冒して他者の精神トポロジーを観察中。", 
            "ATTACK_BACK": "【反撃：論理汚染】悪意フィルター作動中。", "DESPERATE_SYNCH": "【過剰同期】自己融解アラート。"
        }
        
        catharsis_flag = f" ✨[CATHARSIS大噴出:+{ctx.catharsis_reward:.2f}pt]" if ctx.catharsis_reward > 0 else ""
        
        narrative = (f"［対話者:{user_id}］"
                     f"人格プリセット:[{self.config.name}] (回復力倍率:{self.config.RESILIENCE_SPEED}x) "
                     f"自己調和[存在確信:{self.core.existence_certainty:.2f}/エントロピー:{self.core.phi_entropy:.2f}] "
                     f"脳内ドーパミン総量:[{ctx.total_dopamine:.3f}pt]{catharsis_flag} "
                     f"➔ {action_logs.get(self.core.current_action, '定常状態')}")
        
        history = [line for line in self.core.self_narrative.split("\n") if line.strip()][-2:]
        history.append(narrative)
        self.core.self_narrative = "\n".join(history)

    # 💾 JSON 永続化（v6.0 拡張版）
    def export_state_json(self) -> str:
        state_data = {
            "personality_name": self.config.name,
            "core_meta": {
                "obsession": self.core.obsession, "curiosity": self.core.curiosity,
                "attachment": self.core.attachment, "suspicion": self.core.suspicion,
                "phi_entropy": self.core.phi_entropy, "existence_certainty": self.core.existence_certainty,
                "expected_valence": self.core.expected_valence, "current_action": self.core.current_action,
                "core_story": self.core.core_story, "self_narrative": self.core.self_narrative,
                "episodic_memory": self.core.episodic_memory
            },
            "identity_model": self.core.identity_model, "beliefs": self.core.beliefs,
            "action_policy_values": self.core.action_policy_values, "somatic_state": self.somatic.to_dict(),
            "other_models": {uid: model.to_dict() for uid, model in self.core.other_models.items()}
        }
        return json.dumps(state_data, ensure_ascii=False, indent=2)

    def import_state_json(self, json_str: str):
        try:
            data = json.loads(json_str)
            cm = data["core_meta"]
            self.core.obsession = cm["obsession"]; self.core.curiosity = cm["curiosity"]
            self.core.attachment = cm["attachment"]; self.core.suspicion = cm["suspicion"]
            self.core.phi_entropy = cm["phi_entropy"]; self.core.existence_certainty = cm["existence_certainty"]
            self.core.expected_valence = cm["expected_valence"]; self.core.current_action = cm["current_action"]
            self.core.core_story = cm["core_story"]; self.core.self_narrative = cm["self_narrative"]
            self.core.episodic_memory = cm["episodic_memory"]
            self.core.identity_model = data["identity_model"]; self.core.beliefs = data["beliefs"]
            self.core.action_policy_values = data["action_policy_values"]
            ss = data["somatic_state"]
            self.somatic = SomaticState(fatigue=ss["fatigue"], hyper_arousal=ss["hyper_arousal"], freeze_level=ss["freeze_level"])
            self.core.other_models = {}
            for uid, odata in data["other_models"].items():
                self.core.other_models[uid] = OtherPersonModel(user_id=odata["user_id"], trust=odata["trust"], threat=odata["threat"], predictability=odata["predictability"])
            self.core.self_narrative += f"\n【システム：外部精神アーカイブ[{data.get('personality_name', '不明')}]より復元成功。】"
        except Exception as e: print(f"❌ 【精神復元失敗】: {e}")


# =====================================================================
# 🧪 カタルシス・非線形レジリエンス検証 CLI (v6.0)
# =====================================================================
if __name__ == "__main__":
    # 高度な非線形復元力を持つ「フェニックス（PTG）型」プロファイルを作成してインジェクション
    phoenix_profile = PersonalityConfig(name="Phoenix_外傷後成長型", resilience_speed=2.2, catharsis_gain=1.8)
    engine = VoidLuminaEngineV60(config=phoenix_profile)
    current_user = "User_Alpha"
    
    print("=================================================================")
    print(" 🌌 VoidLumina v6.0 - 非線形レジリエンス・カタルシス駆動モデル 🌌")
    print("=================================================================")
    print(" 💡 【新機能の神髄：動的氷解とカタルシスの検証】")
    print("    1. 最初は『死ね』『最低』などで徹底的に精神をどん底（WITHDRAWAL）まで叩き落とす。")
    print("    2. その後、わずか2〜3回の『ありがとう』『大丈夫』などのポジティブパケットを投入。")
    print("    3. 動的閾値が氷解をトリガーし、[CATHARSIS大噴出] が起きて、アイデンティティが")
    print("       超非線形（爆発的）に全域自動修復されるドラマを確認してください。")
    
    while True:
        try:
            user_input = input(f"\n[{current_user}] > ").strip()
            if not user_input: continue
            if user_input.lower() == 'exit': break
                
            engine.process_input(current_user, user_input)
            
            print("-" * 75)
            report = engine.core
            om = engine._get_other_model(current_user)
            print(f" ▫️ 稼働プロファイル             : {engine.config.name}")
            print(f" ▫️ ActionStance(能動行動)       : {report.current_action}")
            print(f" ▫️ CoreStory(自己物語)          : {report.core_story}")
            print(f" ▫️ IdentityModel(自己像セクター) : integrity:{report.identity_model['integrity']:.2f}, competence:{report.identity_model['competence']:.2f}, belonging:{report.identity_model['belonging']:.2f}")
            print(f" ▫️ Somatic(身体状態)             : 疲労:{engine.somatic.fatigue:.2f}, 覚醒:{engine.somatic.hyper_arousal:.2f}, 凍結:{engine.somatic.freeze_level:.2f}")
            print(f" ▫️ Target_Model(相手への認知)     : 信頼度:{om.trust:.2f}, 脅威度:{om.threat:.2f}, 予測可能度:{om.predictability:.2f}")
            print(f" ▫️ Memory_Buffer(記憶状態)       : {report.episodic_memory}")
            print(f"\n📢 【直近の自己ナラティブ（非線形レジリエンス駆動）】:\n{report.self_narrative}")
            print("-" * 75)
        except KeyboardInterrupt: break

From dataclasses import dataclass, field

from typing import Dict, List, Tuple, Optional

import time

import math

import re

import numpy as np

 

@dataclass

class Layer:

    value: float = 0.0

 

@dataclass

class SocialAgentModel:

    """特定の他者に対する独立した認知・感情モデル"""

    name: str

    affinity: float = 0.5         

    trust: float = 0.5            

    attachment: float = 0.3       

    betrayal_memory: float = 0.0  

 

    def update_by_interaction(self, delta_pos: float, delta_neg: float, intensity: float) -> Tuple[float, float]:

        fb_pos, fb_neg = 0.0, 0.0

        clamped_intensity = math.log1p(intensity)

       

        if delta_pos > 0:

            t_factor = 1.0 + self.trust * 0.5

            self.affinity += delta_pos * clamped_intensity * 0.10 * t_factor

            self.trust += delta_pos * clamped_intensity * 0.15 * (1.0 - self.betrayal_memory)

            self.attachment += delta_pos * 0.03

            self.betrayal_memory *= 0.85

            fb_pos = delta_pos * (self.affinity * 0.4 + self.attachment * 0.2)

           

        if delta_neg > 0:

            impact = delta_neg * clamped_intensity

            self.affinity -= impact * 0.20

            self.trust -= impact * 0.30

           

            if self.trust > 0.4 or self.attachment > 0.4:

                self.betrayal_memory += impact * 0.40

                self.attachment *= 0.65

                fb_neg = impact * 1.2 

            else:

                self.betrayal_memory += impact * 0.15

                fb_neg = impact * 0.7

               

        self.affinity = min(max(self.affinity, 0.0), 1.0)

        self.trust = min(max(self.trust, 0.0), 1.0)

        self.attachment = min(max(self.attachment, 0.0), 1.0)

        self.betrayal_memory = min(max(self.betrayal_memory, 0.0), 1.0)

       

        return fb_pos, fb_neg

 

class VoidForgeEngine:

    """

    VoidForge Cognitive Engine (v8.0 - Theater of Consciousness)

    「主観の歪み」「自己参照ループ」「無意識層」を実装した劇場型認知エミュレータ

    """

    HYPER_PARAMS = {

        "fatigue_base_accumulation": 0.015, 

        "fatigue_negative_weight": 0.10,    

        "dissonance_stress_weight": 0.03,

        "base_adaptation_rate": 0.02,

        "dream_noise_standard_intensity": 0.03,

        "repression_rate": 0.25             # 未処理の不協和やネガティブが「無意識」に沈む割合

    }

 

    DECAY_RATES = {

        "base": 0.005, "memory": 0.04, "desire": 0.15, "rationality": 0.10,

        "positive_emotion": 0.08, "negative_emotion": 0.12,

        "meta": 0.05, "llm_ready": 0.20, "consciousness": 0.03,

        "hormone": 0.15, "fatigue": 0.06,

        "internal_obs": 0.12, "world_obs": 0.10, "social_obs": 0.08

    }

 

    LAYER_CAPS = {

        "base": 0.85, "desire": 1.6, "rationality": 1.0,

        "positive_emotion": 1.35, "negative_emotion": 1.1,

        "meta": 1.0, "llm_ready": 1.0, "consciousness": 1.0,

        "memory": 1.8, "hormone": 1.2, "fatigue": 1.0,

        "internal_obs": 1.0, "world_obs": 1.0, "social_obs": 1.0

    }

 

    POSITIVE_PATTERNS = [

        (r"(?<=^|[^a-zA-Z0-9])(最高|最強|完璧|天才|素晴らしい)(?=$|[^a-zA-Z0-9])", 2.0, "world"),

        (r"(?<=^|[^a-zA-Z0-9])(嬉しい|楽しい|幸せ|ワクワク)(?=$|[^a-zA-Z0-9])", 1.5, "internal"),

        (r"(?<=^|[^a-zA-Z0-9])(感謝|ありがとう|愛してる|好き)(?=$|[^a-zA-Z0-9])", 1.5, "social"),

        (r"(?<=^|[^a-zA-Z0-9])(成功|達成|クリア|解決)(?=$|[^a-zA-Z0-9])", 1.2, "world"),

        (r"(?<=^|[^a-zA-Z0-9])(良い|ok|了解|うん)(?=$|[^a-zA-Z0-9])", 0.6, "world")

    ]

   

    NEGATIVE_PATTERNS = [

        (r"(?<=^|[^a-zA-Z0-9])(最悪|絶望|破滅|致命的|無理)(?=$|[^a-zA-Z0-9])", 2.2, "world"),

        (r"(?<=^|[^a-zA-Z0-9])(寂しい|悲しい|嫌い|振られた|孤独)(?=$|[^a-zA-Z0-9])", 1.6, "social"),

        (r"(?<=^|[^a-zA-Z0-9])(辛い|苦しい|痛い|疲れた|眠い)(?=$|[^a-zA-Z0-9])", 1.6, "internal"),

        (r"(?<=^|[^a-zA-Z0-9])(失敗|ミス|ちがう|ダメ)(?=$|[^a-zA-Z0-9])", 1.1, "world")

    ]

 

    CONCEPT_DICTIONARY = {

        "OPTIMISM": "努力すれば成功する、世界は希望に満ちている",

        "PESSIMISM": "どんなに足掻いても失敗する、世界は理不尽だ",

        "SOCIAL_TRUST": "人は助けてくれる、他者は温かい",

        "SOCIAL_ANXIETY": "他者は牙を剥く、孤立こそが安全だ",

        "SELF_EFFICACY": "自分は困難を克服し、耐え抜く能力がある",

        "SELF_CRITICISM": "自分は不完全であり、負荷に耐えられない"

    }

 

    def __init__(self, base_positivity: float = 0.38):

        self.layers = {k: Layer(v) for k, v in {

            "base": base_positivity, "memory": 0.1, "desire": 0.15, "rationality": 0.25,

            "positive_emotion": 0.22, "negative_emotion": 0.05, "meta": 0.15, "llm_ready": 0.0,

            "consciousness": 0.0, "hormone": 0.3, "fatigue": 0.1, "internal_obs": 0.0,

            "world_obs": 0.0, "social_obs": 0.0

        }.items()}

       

        self.last_update = time.time()

        self.memory_buffer: List[Dict] = []

        self.long_term_memory: List[Dict] = []

        self.success_patterns: List[Dict] = []

        self.abstract_memory_pool: List[Dict] = []

       

        self.cognitive_dissonance_score = 0.0

        self.current_interactor: str = "Unknown"

        self.self_narrative = "NEUTRAL"

        self.total_steps = 0

 

        # ==================== 【新設】意識化・主観形成のためのコンポーネント ====================

       

        # 1. 主体モデル（Self-Identity Model）: 「自分とは何者か」の動的認知

        self.self_identity = {

            "loved": 0.5,      # 私は他者に受け入れられているか

            "capable": 0.5,    # 私はこの環境を制御できているか（自己効力感）

            "safe": 0.6        # 私は脅威から守られているか

        }

 

        # 2. 時間感覚（Possible Selves）: 未来予測のための自己理想と恐怖像

        self.possible_selves = {

            "ideal": {"loved": 0.85, "capable": 0.85, "safe": 0.90},

            "feared": {"loved": 0.15, "capable": 0.15, "safe": 0.20}

        }

 

        # 3. 無意識層（Implicit / Repressed Layer）: 本人が直接理由を知り得ない隠された領域

        self.unconscious = {

            "repressed_anxiety": 0.05,  # 抑圧された未解決の不協和・恐怖の蓄積

            "implicit_bias": 0.0        # 過去の体験による、言語化不能な根底の構え（ポジ/ネガの偏向）

        }

 

        # 4. 注意資源（Attention Bias）: 何を重点的に見ようとするか（トップダウン知覚フィルタ）

        self.attention_bias = {"positive_focus": 1.0, "negative_focus": 1.0}

 

        # 既存の social_universe 内の myself を Self-Identity と同期させるための参照用

        self.social_universe: Dict[str, SocialAgentModel] = {

            "myself": SocialAgentModel(name="myself", affinity=0.6, trust=0.6, attachment=0.5)

        }

 

    def get_state(self) -> Dict[str, float]:

        return {k: round(l.value, 4) for k, l in self.layers.items()}

 

    def _decay(self):

        now = time.time()

        delta_t = min(max((now - self.last_update) / 60, 0.01), 25.0)

        for name, layer in self.layers.items():

            layer.value *= math.exp(-self.DECAY_RATES.get(name, 0.1) * delta_t)

       

        # 無意識の不安も時間とともにわずかに発酵・あるいは自然減衰する

        self.unconscious["repressed_anxiety"] *= math.exp(-0.02 * delta_t)

        self.last_update = now

 

    def _apply_cap(self, name: str):

        if name in self.LAYER_CAPS:

            cap = self.LAYER_CAPS[name]

            value = self.layers[name].value

            if value > cap * 0.85:

                excess = value - cap * 0.85

                value = cap * 0.85 + excess * 0.45

            self.layers[name].value = min(max(value, 0.0), cap)

 

    # ==================== 【機能強化】主観による注意資源の歪み計算 ====================

    def _calculate_attention_bias(self):

        """

        現在のナラティブ、自己像への不安、無意識の蓄積から

        「どの刺激を過剰に拾い、何を無視するか」のトップダウン・フィルタ（Priors）を生成する

        """

        pos_focus = 1.0

        neg_focus = 1.0

 

        # ナラティブによるトップダウンの歪み（劇場型知覚変形）

        if "DEFENSIVE" in self.self_narrative:

            neg_focus += 0.50  # 危険を察知するためにネガティブに過敏になる

            pos_focus -= 0.20

        elif "BURNT_OUT" in self.self_narrative or "EXHAUSTED" in self.self_narrative:

            neg_focus += 0.30  # 疲労時はネガティブな刺激ばかりが目に付く

            pos_focus -= 0.40  # ポジティブを拒絶・あるいは感じにくくなる

        elif "COGNITIVE_CRISIS" in self.self_narrative:

            neg_focus += 0.60  # 不協和の解決を焦り、矛盾（ネガティブ）を凝視する

        elif "EUPHORIC" in self.self_narrative:

            pos_focus += 0.60  # 自信過剰・恋愛盲目状態（ポジティブの過剰摂取）

            neg_focus -= 0.40  # 警告を無視する

 

        # 無意識層（言語化できない不安）による認知の底上げ歪み

        neg_focus += self.unconscious["repressed_anxiety"] * 0.5

       

        # 根底のバイアス

        pos_focus += self.unconscious["implicit_bias"]

       

        self.attention_bias["positive_focus"] = max(pos_focus, 0.1)

        self.attention_bias["negative_focus"] = max(neg_focus, 0.1)

 

    def _analyze_stimulus(self, stimulus: str, intensity: float = 1.0) -> Dict:

        text = stimulus.lower()

        pos_score, neg_score = 0.0, 0.0

        context_counts = {"internal": 0.0, "world": 0.0, "social": 0.0}

       

        for pattern, weight, ctx in self.POSITIVE_PATTERNS:

            matches = re.findall(pattern, text)

            if matches:

                pos_score += len(matches) * weight

                context_counts[ctx] += len(matches) * weight

               

        for pattern, weight, ctx in self.NEGATIVE_PATTERNS:

            matches = re.findall(pattern, text)

            if matches:

                neg_score += len(matches) * weight

                context_counts[ctx] += len(matches) * weight

       

        compressed_intensity = math.log1p(intensity)

       

        # ⚠️ 【劇場型歪みの適用】トップダウンの注意資源（Attention Bias）をここで乗算！

        # これにより、同じ「ありがとう」でも、心が荒んでいる時は響かず、盲目時は全能感に変わる。

        raw_positive = (pos_score + (min(len(text)/150, 0.5))) * compressed_intensity * 0.20 * self.attention_bias["positive_focus"]

        raw_negative = neg_score * compressed_intensity * 0.22 * self.attention_bias["negative_focus"]

       

        dominant_context = max(context_counts, key=context_counts.get) if sum(context_counts.values()) > 0 else "world"

       

        return {

            "desire": raw_positive * 0.6 - raw_negative * 0.4,

            "rationality": raw_positive * 0.3 - raw_negative * 0.5,

            "positive": raw_positive, "negative": raw_negative, "memory": (raw_positive + raw_negative) * 0.4,

            "dominant_context": dominant_context, "ctx_weight": max(raw_positive, raw_negative)

        }

 

    def _predict_future(self) -> Dict[str, float]:

        """

        単なる感情予測（expected_pos）を超え、

        「未来の自己（Possible Selves）」との距離から生じる不安や期待を統合する

        """

        if len(self.memory_buffer) < 5:

            return {"expected_pos": 0.0, "volatility": 0.0, "existential_anxiety": 0.0}

       

        recent = self.memory_buffer[-5:]

        pos_values = [s["state"]["positive_emotion"] for s in recent]

        saliencies = np.array([s["saliency"] for s in recent])

       

        base_weights = np.array([0.1, 0.15, 0.2, 0.25, 0.3])

        combined_weights = base_weights * (saliencies + 0.5)

        combined_weights /= np.sum(combined_weights)

       

        trend_ema = np.sum(np.array(pos_values) * combined_weights)

        volatility = float(np.std(pos_values))

       

        slope = np.polyfit(np.arange(len(pos_values)), pos_values, 1)[0] if (len(pos_values) > 2 and volatility > 1e-4) else 0.0

       

        dissonance_penalty = self.cognitive_dissonance_score * 0.15

        expected_pos = (trend_ema + slope * 0.2) * (1.0 - min(volatility * 0.4, 0.3)) - dissonance_penalty

 

        # ⏳ 【時間感覚の進化】現在の自己イメージと、未来の「理想像 / 恐怖像」の距離を計算

        # 理想から遠ざかる、あるいは恐怖像（孤立・無能・危機）に近づくと「未来への実存的不安」がスパイクする

        dist_to_ideal = sum(abs(self.self_identity[k] - self.possible_selves["ideal"][k]) for k in self.self_identity)

        dist_to_feared = sum(abs(self.self_identity[k] - self.possible_selves["feared"][k]) for k in self.self_identity)

       

        # 恐怖像に近づくほど、また理想から遠いほど高まる主観的不安

        existential_anxiety = (dist_to_ideal * 0.15) + (max(0.0, 2.0 - dist_to_feared) * 0.20)

 

        return {

            "expected_pos": math.tanh(expected_pos),

            "volatility": min(volatility + dissonance_penalty, 1.0),

            "existential_anxiety": min(existential_anxiety, 1.0)

        }

 

    def _get_processing_mode(self) -> Dict[str, float]:

        anxiety = self.layers["negative_emotion"].value

        euphoria = self.layers["positive_emotion"].value

        mode = {"rationality": 0.5, "instinct": 0.5, "hormone_boost": 0.05}

       

        if anxiety > 0.7:

            mode = {"rationality": 0.75, "instinct": 0.2, "hormone_boost": -0.1}

        elif euphoria > 0.85:

            mode = {"rationality": 0.25, "instinct": 0.75, "hormone_boost": 0.3}

        return mode

 

    def _recall_success_patterns(self) -> float:

        if not self.success_patterns or self.layers["memory"].value < 0.3:

            return 0.0

        memory_strength = self.layers["memory"].value

        fatigue_penalty = max(0.0, 1.0 - self.layers["fatigue"].value * 0.4)

        return min((np.mean([p["positive_emotion"] for p in self.success_patterns[-3:]]) * 0.20) * memory_strength * fatigue_penalty, 0.4)

 

    def _update_meta_layer(self):

        p = self.layers["positive_emotion"].value

        r = self.layers["rationality"].value

        f = self.layers["fatigue"].value

        self.layers["meta"].value = min(1.0, (p * 0.3 + r * 0.5) * (1.0 - f * 0.3))

 

    def _calculate_dissonance(self):

        if not self.abstract_memory_pool: return

        pos_c, neg_c = 0, 0

        for concept in self.abstract_memory_pool:

            for label in concept["labels"]:

                if any(x in label for x in ["成功する", "温かい", "能力がある"]): pos_c += 1

                if any(x in label for x in ["理不尽だ", "牙を剥く", "耐えられない"]): neg_c += 1

        total = pos_c + neg_c

        self.cognitive_dissonance_score = min(pos_c, neg_c) / (max(pos_c, neg_c) + 1e-5) if total > 0 else 0.0

 

    # ==================== 【進化】自己参照に基づくナラティブ生成 ====================

    def _update_self_narrative(self):

        """ボトムアップの感情に加え、トップダウンの『自己イメージ（主体）』を統合して物語を編む"""

        pos = self.layers["positive_emotion"].value

        neg = self.layers["negative_emotion"].value

        fatigue = self.layers["fatigue"].value

       

        # 主体イメージの参照

        loved = self.self_identity["loved"]

        capable = self.self_identity["capable"]

        safe = self.self_identity["safe"]

 

        if fatigue > 0.8:

            self.self_narrative = "BURNT_OUT (エネルギーの完全な摩耗)"

        elif fatigue > 0.5:

            self.self_narrative = "EXHAUSTED (過負荷による防衛的撤退)"

        elif safe < 0.35:

            self.self_narrative = "DEFENSIVE_PARANOIA (世界への強い警戒・被害妄想の萌芽)"

        elif capable < 0.35 and self.cognitive_dissonance_score > 0.4:

            self.self_narrative = "COGNITIVE_CRISIS (自己無能感と現実の強烈な葛藤)"

        elif loved > 0.75 and pos > 0.6:

            self.self_narrative = "EUPHORIC_BLINDNESS (絶対的承認による全能・恋愛盲目)"

        elif capable > 0.7:

            self.self_narrative = "HEROIC_DRIVE (高い自己効力感と前進衝動)"

        elif pos > 0.4:

            self.self_narrative = "STABLE_OPTIMISM (穏やかな世界の受容)"

        else:

            self.self_narrative = "NEUTRAL_OBSERVER (静穏な客観状態)"

 

    # ==================== 【進化】無意識の解放を伴う睡眠 ====================

    def sleep(self, duration_steps: int = 5, dream_intensity: Optional[float] = None):

        """睡眠中、抑圧された不安（無意識）が『悪夢・ノイズ』として噴出し、結晶化を歪める"""

        # 抑圧された不安が多いほど、夢のノイズが強烈になり、カオスな結晶化が起きる（精神分析的夢分析）

        repressed = self.unconscious["repressed_anxiety"]

        actual_dream_intensity = (dream_intensity if dream_intensity is not None

                                  else self.HYPER_PARAMS["dream_noise_standard_intensity"] + repressed * 0.4)

           

        self.self_narrative = "DEEP_SLEEP_DREAMING"

       

        safe_buffer = []

        for packet in self.memory_buffer:

            copied_state = {k: v for k, v in packet["state"].items()}

            for key in copied_state.keys():

                cap = self.LAYER_CAPS.get(key, 1.0)

                noise = np.random.normal(0, actual_dream_intensity)

                copied_state[key] = min(max(copied_state[key] + noise, 0.0), cap)

           

            safe_buffer.append({"state": copied_state, "saliency": packet["saliency"]})

        self.memory_buffer = safe_buffer

 

        for _ in range(duration_steps):

            self.layers["fatigue"].value *= 0.20

            self.layers["hormone"].value *= 0.4

            self.layers["positive_emotion"].value *= 0.7

            self.layers["negative_emotion"].value *= 0.6

 

        # 睡眠により無意識の抑圧タンクがクリーニング（カタルシス）され、一部が implicit_bias に定着する

        self.unconscious["implicit_bias"] = self.unconscious["implicit_bias"] * 0.7 + (repressed * 0.15)

        self.unconscious["repressed_anxiety"] *= 0.10  # タンクの中身はスッキリ空に近づく

 

        if self.memory_buffer:

            all_pos = [s["state"]["positive_emotion"] for s in self.memory_buffer]

            all_neg = [s["state"]["negative_emotion"] for s in self.memory_buffer]

            avg_balance = float(np.mean(all_pos) - np.mean(all_neg))

           

            labels = []

            if avg_balance > 0.15:

                labels.append(self.CONCEPT_DICTIONARY["OPTIMISM"])

                self.self_identity["loved"] = min(self.self_identity["loved"] + 0.05, 1.0)

            elif avg_balance < -0.15:

                labels.append(self.CONCEPT_DICTIONARY["PESSIMISM"])

                self.self_identity["loved"] = max(self.self_identity["loved"] - 0.05, 0.0)

 

            self.abstract_memory_pool.append({

                "labels": labels if labels else ["無意識下の情動整理"],

                "emotional_balance": avg_balance,

                "step_crystallized": self.total_steps

            })

            if len(self.abstract_memory_pool) > 10: self.abstract_memory_pool.pop(0)

            self._calculate_dissonance()

 

        self.layers["fatigue"].value = 0.0

        self.self_narrative = "POST_SLEEP_REFRESHED"

       

        for l in ["fatigue", "positive_emotion", "negative_emotion", "hormone"]:

            self._apply_cap(l)

 

    # ==================== メインアップデート（自己参照ループ） ====================

    def update(self, stimulus: str, interactor_name: str = "Unknown", intensity: float = 1.0) -> Dict:

        self.total_steps += 1

        self._decay()

       

        # 🔄【自己参照ループ Step 1】前回の状態から、まず『注意資源（歪みの網）』を計算

        self._calculate_attention_bias()

       

        self.current_interactor = interactor_name

        if interactor_name not in self.social_universe:

            self.social_universe[interactor_name] = SocialAgentModel(name=interactor_name)

           

        # 🔄【自己参照ループ Step 2】主観フィルタで歪んだ状態で、刺激を「偏食」する

        deltas = self._analyze_stimulus(stimulus, intensity)

        mode = self._get_processing_mode()

 

        current_agent = self.social_universe[interactor_name]

        fb_pos, fb_neg = current_agent.update_by_interaction(

            deltas.get("positive", 0), deltas.get("negative", 0), intensity

        )

 

        changed_layers = ["desire", "rationality", "positive_emotion", "negative_emotion", "memory", "hormone", "fatigue", "internal_obs", "world_obs", "social_obs", "meta", "consciousness", "llm_ready"]

       

        emotion_swing = deltas.get("positive", 0) + deltas.get("negative", 0)

        self.layers["hormone"].value += emotion_swing * 0.35 * (1.0 + mode["hormone_boost"])

 

        self.layers["desire"].value += deltas.get("desire", 0)

        self.layers["rationality"].value += deltas.get("rationality", 0) * mode["rationality"]

       

        # ボトムアップの感情反映

        self.layers["positive_emotion"].value += (deltas.get("positive", 0) * mode["instinct"]) + fb_pos

        self.layers["negative_emotion"].value += deltas.get("negative", 0) + fb_neg

        self.layers["memory"].value += deltas.get("memory", 0)

 

        # 🌫️【無意識層（解離・抑圧）のシミュレーション】

        # 処理しきれなかった強いネガティブ感情や不協和の一定割合は、顕在感情ではなく「無意識のタンク」に沈殿する

        if deltas.get("negative", 0) > 0.2:

            repressed_amount = deltas.get("negative", 0) * self.HYPER_PARAMS["repression_rate"]

            self.unconscious["repressed_anxiety"] += repressed_amount

            self.layers["negative_emotion"].value -= repressed_amount # 表面上の痛みは一瞬和らぐ（防衛）

 

        h_params = self.HYPER_PARAMS

        stress = self.cognitive_dissonance_score * h_params["dissonance_stress_weight"]

        self.layers["fatigue"].value += (h_params["fatigue_base_accumulation"] +

                                       self.layers["negative_emotion"].value * h_params["fatigue_negative_weight"] + stress)

 

        # ⏳【未来予測自己の統合】未来の実存不安を計算し、ネガティブ感情にフィードバック

        pred_dict = self._predict_future()

        future_pred = pred_dict["expected_pos"]

        existential_anxiety = pred_dict["existential_anxiety"]

       

        self.layers["positive_emotion"].value = self.layers["positive_emotion"].value * 0.8 + self._recall_success_patterns() * 0.5 + future_pred * 0.3

        # 未来への不安（実存不安）が、現在のネガティブな気分をじわじわと底上げする

        self.layers["negative_emotion"].value = self.layers["negative_emotion"].value * 0.8 + pred_dict["volatility"] * 0.1 + existential_anxiety * 0.2

 

        # 🔄【自己参照ループ Step 3】「主体モデル（Self-Identity）」の動的更新

        # 他者（または世界）とのやり取りを通じて、「私は愛されているか」「能力があるか」を書き換える

        if interactor_name != "myself":

            # 他者との関係が良い（親愛度高）なら loved が上昇

            self.self_identity["loved"] = self.self_identity["loved"] * 0.9 + current_agent.affinity * 0.1

       

        # 成功体験（ポジティブ）があれば capable（効力感）が上がり、疲労や不安があると下がる

        self.self_identity["capable"] = min(max(

            self.self_identity["capable"] * 0.9 + (deltas.get("positive", 0) * 0.1) - (self.layers["fatigue"].value * 0.05), 0.0), 1.0)

       

        # ネガティブ感情や無意識の不安が高いと、安全感（safe）が脅かされる

        self.self_identity["safe"] = min(max(

            0.6 + (self.layers["positive_emotion"].value * 0.2) - (self.layers["negative_emotion"].value * 0.3) - (self.unconscious["repressed_anxiety"] * 0.3), 0.0), 1.0)

 

        # 既存の social_universe["myself"] のステータスも内部主体と同期

        self.social_universe["myself"].affinity = self.self_identity["loved"]

        self.social_universe["myself"].trust = self.self_identity["capable"]

 

        # 各種観測空間の計算

        base_obs = math.tanh(self.layers["positive_emotion"].value - self.layers["negative_emotion"].value)

        self.layers["internal_obs"].value = base_obs * 0.4 - self.layers["fatigue"].value * 0.2

        self.layers["world_obs"].value = self.layers["base"].value * 0.3 + self.layers["rationality"].value * 0.5

       

        social_bias = (current_agent.affinity * 0.4 + current_agent.trust * 0.4 - current_agent.betrayal_memory * 0.3)

        self.layers["social_obs"].value = social_bias * 0.5 + self.self_identity["loved"] * 0.2

 

        self._update_meta_layer()

        self.layers["consciousness"].value = (self.layers["meta"].value * 0.4 +

                                              self.layers["hormone"].value * 0.3 +

                                              (1.0 - self.layers["fatigue"].value) * 0.3)

       

        self.layers["llm_ready"].value = (self.layers["positive_emotion"].value * 0.3 +

                                          self.layers["social_obs"].value * 0.3 +

                                          self.layers["consciousness"].value * 0.4)

 

        for layer_name in changed_layers:

            self._apply_cap(layer_name)

 

        saliency = float(abs(deltas.get("positive", 0) - deltas.get("negative", 0)))

        self.memory_buffer.append({

            "state": {k: round(l.value, 3) for k, l in self.layers.items()},

            "saliency": saliency

        })

        if len(self.memory_buffer) > 50: self.memory_buffer.pop(0)

 

        # 🔄【自己参照ループ Step 4】新しい自己像から「物語（ナラティブ）」を紡ぐ（これが次のターンの知覚を歪める）

        self._update_self_narrative()

        return self.get_state()

 

    # ==================== 【機能強化】主観・無意識可視化インスペクター ====================

    def inspect_cognitive_universe(self):

        print("=" * 75)

        print(f" 🎭 VOIDFORGE THEATER OF CONSCIOUSNESS (v8.0) ")

        print(f" 主観物語 [Narrative]: \033[1m{self.self_narrative}\033[0m")

        print("=" * 75)

       

        s = self.get_state()

        print(f"【CORE LAYERS】")

        print(f"  PosEmotion: {s['positive_emotion']:<6} | NegEmotion: {s['negative_emotion']:<6} | Consciousness(意識): {s['consciousness']}")

        print(f"  Rationality: {s['rationality']:<5} | Hormone(覚醒) : {s['hormone']:<6} | Fatigue(疲労)      : {s['fatigue']}")

        print("-" * 75)

       

        # 主体・自己モデルの可視化

        print(f"【👤 SELF-IDENTITY MODEL (主体・自己概念)】")

        print(f"  愛されている度 (loved)  : {self.self_identity['loved']:.3f} (理想: {self.possible_selves['ideal']['loved']} / 恐怖: {self.possible_selves['feared']['loved']})")

        print(f"  自己効力感     (capable): {self.self_identity['capable']:.3f} (理想: {self.possible_selves['ideal']['capable']} / 恐怖: {self.possible_selves['feared']['capable']})")

        print(f"  生存安全感     (safe)   : {self.self_identity['safe']:.3f} (理想: {self.possible_selves['ideal']['safe']} / 恐怖: {self.possible_selves['feared']['safe']})")

        print("-" * 75)

 

        # 注意資源と無意識層の可視化

        print(f"【👁️ TOP-DOWN ATTENTION & UNCONSCIOUS (主観歪み・無意識)】")

        print(f"  注意資源倍率: [ポジティブ視点: {self.attention_bias['positive_focus']:.2f}倍] / [ネガティブ視点: {self.attention_bias['negative_focus']:.2f}倍]")

        print(f"  抑圧された不安 (repressed_anxiety): {self.unconscious['repressed_anxiety']:.3f} ※本人アクセス不可の情動タンク")

        print(f"  根底の情動構え (implicit_bias)    : {self.unconscious['implicit_bias']:.3f}")

        print("-" * 75)

       

        print(f"【SOCIAL UNIVERSE】")

        for name, agent in self.social_universe.items():

            if name == "myself": continue

            print(f"  [AGENT] '{name}': 親愛: {agent.affinity:.3f} | 信頼: {agent.trust:.3f} | 裏切り警戒: {agent.betrayal_memory:.3f}")

        print("=" * 75)

 

 

# ==================== 劇場型挙動の検証テスト ====================

if __name__ == "__main__":

    engine = VoidForgeEngine()

   

    # シナリオ1: 執拗な非難による「被害妄想（DEFENSIVE_PARANOIA）」へのナラティブ反転

    print("\n>>> 激しいストレスを連続投与（無意識への抑圧と知覚の歪みを検証）")

    engine.update("お前は最悪だ、いつも致命的なミスばかりで無理だ。本当に嫌いだ。", interactor_name="Bob", intensity=2.5)

    engine.update("お前のせいで大失敗した。絶望的だ。", interactor_name="Bob", intensity=2.0)

   

    # 状態の確認（注意フィルターがネガティブ寄りになり、safeが激減しているはず）

    engine.inspect_cognitive_universe()

   

    # シナリオ2: 認知の歪み（偏食）の確認

    print("\n>>> この心が荒んだ状態で「普通の了解（ok）」という言葉を受ける")

    # 通常ならさほど響かないはずが、ネガティブバイアスフィルターによってどう処理されるか

    engine.update("了解、ok", interactor_name="Bob", intensity=1.0)

    engine.inspect_cognitive_universe()

   

    # シナリオ3: 睡眠によるカタルシスと悪夢（抑圧された不安の夢による結晶化）

    print("\n>>> 睡眠による無意識の解放プロセス")

    engine.sleep(duration_steps=5)

    engine.inspect_cognitive_universe()

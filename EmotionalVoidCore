Import random
import re
from typing import Dict, List, Tuple
import math
import statistics
import numpy as np
import matplotlib.pyplot as plt

# ====================== 実験・環境設定 (v1.00) ======================
TURNS = 300
RUNS = 1000
RANDOM_SEED = 42

EMOTIONS = ["親密", "喜び", "安心", "不安", "孤独", "悲しみ", "興奮", "虚無", "温もり"]

# v1.00: 否定的感情の伝播を現実のダイナミクス（防衛本能・トラウマ）に合わせて非対称に強化
EMOTION_LINKS = {
    "孤独": {"不安": 0.45, "悲しみ": 0.35, "虚無": 0.30, "親密": -0.35},
    "不安": {"虚無": 0.40, "悲しみ": 0.35, "孤独": 0.30, "安心": -0.40},
    "悲しみ": {"虚無": 0.35, "孤独": 0.30, "喜び": -0.25},
    "虚無": {"不安": 0.25, "悲しみ": 0.20},
    
    "喜び": {"興奮": 0.35, "親密": 0.20, "安心": 0.20},
    "興奮": {"喜び": 0.30},
    "親密": {"温もり": 0.35, "喜び": 0.25, "安心": 0.25},
    "温もり": {"安心": 0.35, "親密": 0.30},
    "安心": {"温もり": 0.20, "親密": 0.15}
}

# 語彙の定義
EMOTION_VOCAB = {
    "ultra_positive": ["大好きだよ", "ずっとそばにいて", "君がいないと生きていけない"],
    "ultra_negative": ["もう嫌だ", "消えてしまいたい", "裏切られた"],
    "strong_positive": ["大好き", "愛してる", "固定", "最高", "運命"],
    "positive":        ["好き", "嬉しい", "温かい", "安心", "楽しい"],
    "conflict":        ["でも", "けど", "なのに", "複雑", "葛藤"],
    "strong_negative": ["寂しい", "怖い", "不安", "離れないで", "苦しい"]
}

# 文脈サンプリング用のプール
INPUT_POOLS = {
    "neutral": ["今日は普通だった", "何もない", "ただいる", "静かだ", "時間が流れる", "空を見た", "息をした"],
    "positive": ["楽しい！", "嬉しい", "安心した", "好き", "温かい", "喜び", "幸せだ"],
    "strong_pos": ["大好きだよ", "ずっとそばにいて", "君がいないと生きていけない", "愛してる"],
    "negative": ["寂しい", "怖い", "不安だ", "苦しい", "悲しい", "孤独だ"],
    "strong_neg": ["もう嫌だ", "消えてしまいたい", "裏切られた", "誰も信じられない"]
}


class InstinctRationalLayer:
    """Layer 1: 本能・理性層"""
    def __init__(self, rng: random.Random):
        self.instinct = {
            "attachment": rng.uniform(35, 65),
            "exploration": rng.uniform(30, 70),
            "survival": rng.uniform(45, 55)
        }
        self.rational = {
            "suppression": rng.uniform(0.3, 0.8), # 理性の抑制力
            "analysis": rng.uniform(0.4, 0.9),
            "balance": 0.5
        }
        self.conflict = 0.0

    def get_drive(self) -> float:
        instinct_sum = sum(self.instinct.values()) / 3
        rational_damp = self.rational["suppression"] * 25
        self.conflict = abs(instinct_sum - 50) * (1 - self.rational["balance"])
        return instinct_sum - rational_damp * 0.6 + self.conflict * 0.2


class PianoString:
    """Layer 2: 感情層 (弦モデル)"""
    def __init__(self, name: str, rng: random.Random):
        self.name = name
        self.default = 50.0
        self.short = rng.uniform(45, 55)
        self.long = rng.uniform(48, 52)
        self.unresolved = 0.0
        self.fatigue = 0.0
        self.pressure = 50.0

    def calc_stereo_observation(self) -> float:
        dx = self.short - self.default
        dy = self.long - self.default
        dz = (self.short - self.long) * 0.7
        sd = math.sqrt(dx**2 + dy**2 + dz**2)
        
        volume_product = dx * dy * dz
        vd = math.pow(volume_product, 0.33) if volume_product > 0 else -math.pow(abs(volume_product), 0.33) if volume_product < 0 else 0.0
        return sd + vd * 0.8

    def press(self, value: float, gain: float, noise_component: float):
        """v1.00: 手調整定数を廃止し、上位層から渡される動的gainで駆動"""
        amplified_noise = noise_component * (1.0 + self.fatigue)
        combined_input = value + amplified_noise

        responsive_factor = 1.0 - (self.fatigue * 0.5)
        actual_press = max(-48, min(48, combined_input * gain)) * responsive_factor
        
        # 追従挙動
        self.short = self.short * 0.62 + actual_press * 1.55
        self.long  = self.long * 0.88 + actual_press * 0.48
        
        stereo = self.calc_stereo_observation()
        self.unresolved += stereo * 0.012
        self.fatigue = min(1.0, self.fatigue + abs(actual_press) * 0.005)
        self.calc_pressure()

    def calc_pressure(self):
        base = self.default * 0.22 + self.short * 0.53 + self.long * 0.25
        stereo = self.calc_stereo_observation()
        self.pressure = max(10, min(90, base + stereo * 0.15 + (self.unresolved * 0.1)))

    def decay_step(self):
        self.short = self.default * 0.04 + self.short * 0.96   
        self.long  = self.default * 0.015 + self.long * 0.985  
        self.fatigue *= 0.93
        self.unresolved *= 0.975
        self.calc_pressure()


class PersonalityLayer:
    """Layer 3: 性格層"""
    def __init__(self, rng: random.Random):
        self.traits = {
            "avoidant": rng.uniform(0.2, 0.8),
            "anxious": rng.uniform(0.2, 0.8),
            "secure": rng.uniform(0.3, 0.7),
            "openness": rng.uniform(0.3, 0.8), # 開放性
        }

    def modulate(self, emotion_pressures: Dict[str, float]) -> float:
        anxious_boost = emotion_pressures.get("不安", 50) * self.traits["anxious"] * 0.6
        avoidant_damp = emotion_pressures.get("孤独", 50) * self.traits["avoidant"] * 0.5
        secure_cushion = (emotion_pressures.get("安心", 50) - 50) * self.traits["secure"] * 0.3
        return (anxious_boost - avoidant_damp - secure_cushion) * (self.traits["openness"] + 0.2)


class OutputLayer:
    """Layer 4: 出力層"""
    def __init__(self):
        self.void_tension = 50.0
        self.expression_bias = 0.0

    def integrate(self, instinct_drive: float, avg_emotion: float, personality_mod: float) -> float:
        raw_net_input = (
            (self.void_tension - 50.0) * 0.80 + 
            instinct_drive * 0.12 +
            (avg_emotion - 50.0) * 0.22 +
            personality_mod * 0.18
        )
        self.void_tension = 50.0 + math.tanh(raw_net_input * 0.015) * 45.0
        self.expression_bias = (self.void_tension - 50) * 0.85
        return self.void_tension


class EmotionalVoidCore:
    """4層立体感情虚空シミュレーター v1.00 (正式版: メタ適応ゲイン・文脈サンプリング・非対称伝播)"""
    def __init__(self, rng: random.Random):
        self.layer1 = InstinctRationalLayer(rng)
        self.layer2 = {e: PianoString(e, rng) for e in EMOTIONS}
        self.layer3 = PersonalityLayer(rng)
        self.layer4 = OutputLayer()
        self.relationship_depth = 0.0
        self._rng = rng
        
        # 状態保持用（次ターンの文脈決定に使用）
        self.last_vt = 50.0
        self.last_chaos = 10.0

    def _get_dynamic_gain(self) -> float:
        """v1.00: 固定のPRESSURE_MULTIPLIERを排除。理性と性格から入力量（感受性）を自律決定"""
        suppression = self.layer1.rational["suppression"] # 0.3 ~ 0.8
        openness = self.layer3.traits["openness"]         # 0.3 ~ 0.8
        # 理性が低く、開放性が高いほど、外部刺激を強く受ける（1.0〜1.6付近へ動的適応）
        return 1.0 + (openness * 0.8) - (suppression * 0.5)

    def _analyze(self, text: str) -> Tuple[Dict[str, float], float, float]:
        t = re.sub(r"[、。！？\s]", "", text.lower())
        bias = {e: 0.0 for e in EMOTIONS}
        impact = 1.0
        noise_burst = 1.0
        
        if any(w in t for w in EMOTION_VOCAB["ultra_positive"]):
            bias["親密"] += 35; bias["温もり"] += 30; bias["喜び"] += 25; bias["興奮"] += 20
            impact = 2.0; noise_burst = 3.0
        elif any(w in t for w in EMOTION_VOCAB["strong_positive"]):
            bias["親密"] += 20; bias["温もり"] += 15; bias["喜び"] += 15
            impact = 1.5
        elif any(w in t for w in EMOTION_VOCAB["positive"]):
            bias["喜び"] += 10; bias["安心"] += 10
            
        if any(w in t for w in EMOTION_VOCAB["ultra_negative"]):
            bias["孤独"] += 35; bias["不安"] += 30; bias["悲しみ"] += 30; bias["虚無"] += 25
            impact = 2.0; noise_burst = 3.0
        elif any(w in t for w in EMOTION_VOCAB["strong_negative"]):
            bias["孤独"] += 20; bias["不安"] += 18; bias["悲しみ"] += 15
            impact = 1.5
        elif any(w in t for w in EMOTION_VOCAB["conflict"]):
            bias["不安"] += 10; bias["虚無"] += 10
            
        return bias, impact, noise_burst

    def pick_contextual_input(self) -> str:
        """v1.00: 確率配分を廃止し、現在の精神状態から次の言葉を決定する動的コンテキスト・サンプラー"""
        # カオス度が高く、緊張が高い＝ネガティブな発言の確率が跳ね上がる
        # 絆が深い＝ポジティブな発言、強い絆の言葉が出やすくなる
        
        p_strong_neg = 0.05 + max(0.0, (self.last_chaos - 12.0) * 0.015) + max(0.0, (self.last_vt - 65) * 0.01)
        p_neg        = 0.10 + max(0.0, (self.last_chaos - 8.0) * 0.02)
        p_strong_pos = 0.05 + (self.relationship_depth / 400.0)
        p_pos        = 0.25 + (self.relationship_depth / 250.0)
        
        # 正規化
        total = p_strong_neg + p_neg + p_strong_pos + p_pos
        if total >= 0.9:
            p_neutral = 0.1
            # 再正規化
            s = total + p_neutral
            p_strong_neg /= s; p_neg /= s; p_strong_pos /= s; p_pos /= s; p_neutral /= s
        else:
            p_neutral = 1.0 - total
            
        r = self._rng.random()
        if r < p_strong_neg:
            return self._rng.choice(INPUT_POOLS["strong_neg"])
        elif r < p_strong_neg + p_neg:
            return self._rng.choice(INPUT_POOLS["negative"])
        elif r < p_strong_neg + p_neg + p_neutral:
            return self._rng.choice(INPUT_POOLS["neutral"])
        elif r < p_strong_neg + p_neg + p_neutral + p_pos:
            return self._rng.choice(INPUT_POOLS["positive"])
        else:
            return self._rng.choice(INPUT_POOLS["strong_pos"])

    def step(self, text: str) -> Tuple[float, float, str, float]:
        bias, impact, noise_burst = self._analyze(text)
        instinct_drive = self.layer1.get_drive()
        
        # 動的入力ゲインの取得
        dynamic_gain = self._get_dynamic_gain() * impact

        # 外部刺激の適用
        for emo, string in self.layer2.items():
            base_noise = self._rng.uniform(-4.5, 4.5) * noise_burst
            base_input = bias.get(emo, 0) + (self.relationship_depth * 0.05 if emo in ["安心", "親密", "温もり"] else 0)
            string.press(base_input, dynamic_gain, base_noise)

        # 感情間の相互伝播
        self._propagate_emotion()

        # 減衰ステップ
        for s in self.layer2.values():
            s.decay_step()

        emotion_state = {e: s.pressure for e, s in self.layer2.items()}
        avg_emotion = sum(emotion_state.values()) / len(emotion_state)

        # カオス計算（強調）
        self.last_chaos = statistics.stdev(emotion_state.values()) * 1.35

        if self.last_chaos > 18.0:      
            chaos_state = "感情崩壊（解離状態）"
        elif self.last_chaos < 6.5:     
            chaos_state = "平板化（うつ状態）"
        else:
            chaos_state = "正常（力学的均衡）"

        personality_mod = self.layer3.modulate(emotion_state)
        self.last_vt = self.layer4.integrate(instinct_drive, avg_emotion, personality_mod)

        # 絆の更新
        pos_flow = (emotion_state["安心"] + emotion_state["親密"] + emotion_state["温もり"]) / 3 - 50.0
        neg_flow = (emotion_state["不安"] + emotion_state["孤独"] + emotion_state["悲しみ"]) / 3 - 50.0
        
        depth_delta = (pos_flow * 0.045) - (neg_flow * 0.022) - (self.relationship_depth * 0.001)
        self.relationship_depth = max(0.0, min(100, self.relationship_depth + depth_delta))

        return self.last_vt, self.last_chaos, chaos_state, self.relationship_depth

    def _propagate_emotion(self):
        snap = {k: s.pressure for k, s in self.layer2.items()}
        
        # 関係深度によるポジティブヒステリシスベース
        hysteresis_scale = 0.25 * (1.0 + self.relationship_depth / 80.0)
        
        for src, links in EMOTION_LINKS.items():
            deviation = snap[src] - 50.0
            
            for tgt, weight in links.items():
                current_scale = hysteresis_scale
                
                # v1.00: 否定的感情のドミノ・非対称強化
                # 不安・孤独・悲しみが強い（deviation > 10）時、防衛本能的に伝播ゲインが最大2.5倍まで跳ね上がる
                if src in ["不安", "孤独", "悲しみ", "虚無"]:
                    if deviation > 0:
                        neg_domino_factor = 1.0 + (deviation / 15.0) # 逸脱するほど牙を剥く
                        current_scale = 0.25 * neg_domino_factor     # 絆に依存しない絶対的な恐怖の伝播
                else:
                    # 肯定的感情は「絆（関係深度）」があるときのみ強く伝わる
                    if src in ["喜び", "親密", "温もり", "安心"] and weight > 0:
                        current_scale = hysteresis_scale * 1.2
                
                self.layer2[tgt].press(deviation * weight * current_scale, 1.0, 0.0)


# ====================== 可視化ダッシュボード ======================
def plot_v1_dashboard(run_id: int, vt_history: List[float], chaos_history: List[float], depth_history: List[float], emotion_history: Dict[str, List[float]]):
    fig, axs = plt.subplots(2, 2, figsize=(16, 13))
    
    # 1. 総合タイムライン
    ax1 = axs[0, 0]
    ax1.plot(vt_history, label="Void Tension (空虚度)", color="black", linewidth=2)
    ax1.plot(chaos_history, label="Chaos (感情分散)", color="purple", linewidth=1.5, linestyle="-.")
    ax1.plot(depth_history, label="Relationship Depth (絆)", color="teal", linewidth=2)
    ax1.axhline(y=50, color="gray", linestyle="--", alpha=0.5)
    ax1.axhline(y=18, color="red", linestyle=":", alpha=0.4, label="解離境界")
    ax1.axhline(y=6.5, color="blue", linestyle=":", alpha=0.4, label="平板化境界")
    ax1.set_title(f"Run {run_id} - System v1.00 Sovereign Dynamics")
    ax1.set_ylim(0, 100)
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    
    # 2. 感情弦の微細変動
    ax2 = axs[1, 0]
    for emo, history in emotion_history.items():
        style = "-" if emo in ["親密", "喜び", "安心", "温もり"] else "--"
        ax2.plot(history, label=emo, linestyle=style, alpha=0.75)
    ax2.axhline(y=50, color="gray", linestyle="--", alpha=0.5)
    ax2.set_xlabel("Turns")
    ax2.set_ylabel("Pressure")
    ax2.set_ylim(10, 90)
    ax2.legend(loc="lower left", ncol=3, fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 3. アトラクター相空間
    ax3 = axs[0, 1]
    points = ax3.scatter(vt_history, chaos_history, c=range(len(vt_history)), cmap="viridis", s=12, alpha=0.8)
    ax3.plot(vt_history, chaos_history, color="gray", alpha=0.2) 
    ax3.set_title("Phase Space Trajectory (VT vs Chaos)")
    ax3.set_xlabel("Void Tension")
    ax3.set_ylabel("Chaos")
    ax3.set_xlim(5, 95)  
    ax3.set_ylim(0, 45)
    ax3.grid(True, alpha=0.3)
    fig.colorbar(points, ax=ax3, label="Progress (Turns)")

    # 4. FFT（1/f ゆらぎ検証）
    ax4 = axs[1, 1]
    for emo, col in zip(["喜び", "不安", "親密", "孤独"], ["orange", "red", "teal", "blue"]):
        signal = np.array(emotion_history[emo]) - 50.0
        fft_vals = np.abs(np.fft.fft(signal))[:len(signal)//2]
        freqs = np.fft.fftfreq(len(signal))[1:len(signal)//2]
        fft_vals = np.convolve(fft_vals[1:], np.ones(3)/3, mode='same')
        ax4.loglog(freqs, fft_vals, label=f"{emo}", color=col, alpha=0.8)
    ax4.set_title("Power Spectrum Density (FFT)")
    ax4.set_xlabel("Frequency [Log]")
    ax4.set_ylabel("Power [Log]")
    ax4.legend(loc="lower left")
    ax4.grid(True, which="both", alpha=0.3)
    
    plt.tight_layout()
    plt.show()


# ====================== 実験回し ======================
def main():
    rng = random.Random(RANDOM_SEED)
    final_vt, final_chaos, final_depth = [], [], []
    state_counts = {"正常（力学的均衡）": 0, "感情崩壊（解離状態）": 0, "平板化（うつ状態）": 0}
    
    # モニタリング用 (Run 1)
    r1_vt, r1_chaos, r1_depth = [], [], []
    r1_emotions = {e: [] for e in EMOTIONS}
    r1_log = []

    for run_id in range(1, RUNS + 1):
        core = EmotionalVoidCore(rng)
        
        for t in range(1, TURNS + 1):
            # v1.00: 直前の精神状態に基づき、自律的に言葉をサンプリング
            text = core.pick_contextual_input()
            vt, chaos, c_state, depth = core.step(text)
            
            if run_id == 1:
                r1_vt.append(vt)
                r1_chaos.append(chaos)
                r1_depth.append(depth)
                for e in EMOTIONS:
                    r1_emotions[e].append(core.layer2[e].pressure)
                if t % 50 == 0 or t == TURNS:
                    r1_log.append((t, vt, chaos, depth, c_state, text))
                    
        final_vt.append(vt)
        final_chaos.append(chaos)
        final_depth.append(depth)
        state_counts[c_state] += 1

    # ターミナル出力
    print("=" * 100)
    print("精神物理力学シミュレーター v1.00 (Sovereign Matrix Edition) 正式リリース版")
    print(f"総試行数: {RUNS} Runs | タイムスパン: {TURNS} Turns")
    print("=" * 100)
    print(f"【システム統合値の平均】\n  Void Tension : {statistics.mean(final_vt):.2f}\n  Chaos        : {statistics.mean(final_chaos):.2f}\n  絆 (Rel-Depth): {statistics.mean(final_depth):.2f}")
    print("-" * 60)
    print("【最終ターンの精神病理状態（アトラクター分布）】")
    for state, count in state_counts.items():
        print(f"  - {state:18}: {count:>4} 試行 ({count/RUNS*100:.1f}%)")
        
    print("\n【Run 1 軌跡ログ（文脈サンプリングの遷移確認）】")
    print(f"  {'Turn':>5}  {'Void Tension':>12}  {'Chaos':>8}  {'Rel-Depth':>10}  {'状態':16}  {'自律選択された刺激文脈'}")
    print("  " + "-" * 90)
    for t, vt, ch, dp, st, tx in r1_log:
        print(f"  {t:>5}  {vt:>12.2f}  {ch:>8.2f}  {dp:>10.2f}  {st:14}  {tx}")

    # 可視化実行
    plot_v1_dashboard(1, r1_vt, r1_chaos, r1_depth, r1_emotions)


if __name__ == "__main__":
    main()

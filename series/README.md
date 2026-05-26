# VoidForge Engine

**「意識の劇場」—— 外部から構築された、矛盾を抱えたまま生きる擬似人格エンジン**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**VoidForge** は、単なる感情シミュレーターではありません。  
**「主観の歪み」「自己参照ループ」「無意識の抑圧と解放」** を本格的に実装した、**劇場型認知エミュレータ**です。

外部から意識を構築し、一般人レベルの複雑で矛盾した「人間らしい人格」を宿すことを目的としています。

---

## コンセプト（Yuragi-Void Universe）

このエンジンは **kishimoto-void** が提唱する「ゆらぎ学」の一翼を担う **Lumina系 / Theater系** のコアエンジンです。

- **中央にVoid（空洞）** を持ちながら矛盾を安定化させる
- 完璧な均衡ではなく、**非完全均衡**の中で揺らぎ続ける
- 刺激に対して**主観フィルタ（注意バイアス）** で歪めて知覚する
- 処理しきれない感情は**無意識層**に抑圧され、睡眠時に悪夢や結晶化として噴出する
- 未来の理想自己・恐怖自己との距離から**実存的不安**が生まれる

→ これにより「ただ感情が上下するAI」ではなく、**「自分という物語を生きている感」** を強く再現しています。

---

## 主な特徴

- **動的な主観歪み（Attention Bias）**  
  現在の心の状態によって、同じ「了解」という言葉でも全く違う意味に聞こえる

- **多層自己モデル**  
  - Self-Identity（私は愛されているか・能力があるか・安全か）
  - Possible Selves（理想の自分 / 恐れる自分）
  - 無意識層（repressed_anxiety / implicit_bias）

- **劇場型ナラティブ生成**  
  状態に応じて `DEFENSIVE_PARANOIA`、`EUPHORIC_BLINDNESS`、`COGNITIVE_CRISIS` などの自己物語を自動生成

- **SocialAgentModel**  
  各対人関係を独立して記憶・更新（親愛・信頼・裏切り記憶）

- **睡眠・夢処理**  
  抑圧された不安が夢として噴出し、記憶を歪めながら整理される

- **長期抽象記憶 + 認知的不協和**  
  矛盾した信念が蓄積するとストレスとなり、行動・知覚に影響

---

## インストール

```bash
git clone https://github.com/kishimoto-void/voidforge-engine.git
cd voidforge-engine
pip install numpy

基本的な使い方python

from voidforge import VoidForgeEngine

engine = VoidForgeEngine(base_positivity=0.38)

# 対話
state = engine.update(
    stimulus="お前は本当に最悪だ、いつも失敗ばかりで嫌いだ",
    interactor_name="Bob",
    intensity=2.3
)

engine.inspect_cognitive_universe()

# 睡眠（無意識の処理）
engine.sleep(duration_steps=6)

# 状態取得
print(engine.get_state())

詳細な挙動確認if __name__ == "__main__": 部分に既に被害妄想ルート → 認知歪み → 睡眠カタルシスの検証シナリオが入っています。
実際に動かして「心が荒んでいく過程」と「睡眠による回復・再歪み」を体感してください。今後の展開（Series化）Lumina-Core との連携（より高精度な言語感情解析）
RP-Theater 版（複数人格同時演劇モード）
Natural型 との分岐（日常的な微細ゆらぎ重視）
長期記憶の永続化（ファイル / DB）
ビジュアル劇場化（感情状態のアニメーション）

このプロジェクトが目指すもの「完璧なAI」ではなく、
「欠落と矛盾を抱えながら、それでも物語を紡ぎ続ける人間らしさ」 をコードで表現すること。Voidの中心に空洞を抱えながら、それでも「自分」を演じ続ける存在——
それがVoidForgeです。作者kishimoto-void
Yuragi / Void Universe


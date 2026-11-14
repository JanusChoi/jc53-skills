# vision_analyze 结构化提问模板

用 vision_analyze 工具（agent 自带）看 qc_frames/*.png 时，按下面模板问。每个问句都设计成"是/否"或可量化回答，方便汇总到 qc_report.json。

## 通用模板（所有 videomaker 集适用）

对每段 take 的 3 帧（首/中/末）问这 6 题：

### 1. 角色在场
"画面里能看到两只猫吗？一只黑白相间（戴金圆框眼镜、穿深蓝围裙），一只三花（戴浅金棕色平顶宽檐草帽）。分别用'清晰可见 / 模糊可见 / 缺失'三个等级描述。"

### 2. 角色比例
"两只猫的体型是否符合预期？是否出现了'一只猫明显比另一只大 3 倍以上'的失真？"

### 3. 场景匹配
"画面背景是否符合 prompt 描述？（eg 室内暖黄台灯 + 窗外冷蓝月光）整体色温是否暖冷对比清晰？"

### 4. 雪质感（仅雪/雨/雾场景）
"画面里的雪是'蓬松粒状颗粒'还是'棉花光斑/模糊光点'？用一句话描述雪的视觉感受。"

### 5. 构图
"主体（猫 / 道具）是否在画面中央偏左/偏右？是否有'被切掉一半'或'贴在边缘'的构图问题？"

### 6. 异常元素
"画面里有没有出现 prompt 没要求的元素？（eg 凭空出现的猫脸涂鸦、人类手指、文字 logo）"

## 汇总模板

每段 take 的 6 题答案合成一个 dict：

```json
{
  "seg1_take1": {
    "frame_count": 3,
    "vision": [
      {"frame": "frame_00.png", "q1_characters": "墨团清晰，豆沙清晰", "q2_proportion": "正常", "q3_scene": "窗前暖光对冷光", "q4_snow": "颗粒状 OK", "q5_composition": "OK", "q6_anomaly": "无"},
      ...
    ],
    "verdict": "pass"
  }
}
```

verdict 规则：
- 任何帧 q1 角色缺失 → verdict: `retry`
- 任何帧 q4 雪质感失败 → verdict: `retry`
- 任何帧 q6 异常元素（且不是 prompt 要求） → verdict: `review`
- 其他全过 → verdict: `pass`

## 提问风格注意事项

1. **明确特征描述**：不要问"墨团在不在"——问"戴金圆框眼镜、穿深蓝围裙的黑白猫在不在"。vision 看到的猫没有"名字"，只有视觉特征。
2. **避免开放问题**：不要问"画面怎么样"，要问"色温是暖还是冷"——后者才能给出确定答案。
3. **一次问 6 个问题**：一次 vision_analyze 调用问多题比分 6 次调更省 token。
4. **跟 qc_signals 互补**：signals 给出客观（时长/sharpness/diff），vision 给出主观（角色/构图/异常）。两者冲突时以 vision 为准（signals 只是 sanity check）。

## 猫系列专属 prompts（cat-01 ~ cat-04）

跟"雪猫"系列对齐：
- 墨团：黑白相间（white blaze between eyes, white muzzle/chest/belly/paws）+ 金圆框眼镜 + 深蓝围裙
- 豆沙：白/橙/黑三花 + 浅金棕平顶宽檐草帽 + 略歪右
- 雪质感：蓬松粒状、不是棉花

把这段直接贴进 vision_analyze 的 question 里。

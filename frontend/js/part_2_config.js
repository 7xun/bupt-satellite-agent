// part_2_config.js - 图表分组与阈值配置
const part_2_chart_config = {
    groups: [
        {
            id: "power_bus",
            title: "母线与蓄电池电压电流",
            indicators: ["母线电压", "母线电流", "蓄电池电流", "蓄电池电压"],
            thresholds: { lower: -5, upper: 5 }
        },
        {
            id: "uplink_cmd",
            title: "上注指令计数",
            indicators: ["上注指令接收计数", "上注指令执行计数", "上注指令错误计数"],
            thresholds: { lower: -5, upper: 5 }
        },
        {
            id: "temperature",
            title: "关键温度监测",
            indicators: ["整机温度", "蓄电池测温1", "+Y舱板星内表面ADSB耳片温度", "测控单机-Y侧安装面温度"],
            thresholds: { lower: -5, upper: 5 }
        },
        {
            id: "vdes_bus",
            title: "VDES总线无应答计数",
            indicators: ["主VDES总线无应答计数", "备VDES总线无应答计数"],
            thresholds: { lower: -5, upper: 5 }
        }
    ],
    thresholdStyle: {
        lineColor: "#e67e22",
        fillColor: "rgba(230, 126, 34, 0.08)",
        dash: [6, 6],
        lineWidth: 1
    }
};

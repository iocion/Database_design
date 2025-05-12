document.getElementById("conditionForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    // 清空之前的内容
    document.getElementById("error").style.display = "none";
    document.getElementById("thinking").style.display = "none";
    document.getElementById("result").style.display = "none";
    
    const condition = document.getElementById("condition").value;
    const thinkingDiv = document.getElementById("thinking");
    const reasoningDiv = document.getElementById("reasoning");
    const resultDiv = document.getElementById("result");
    const conditionResult = document.getElementById("conditionResult");
    const adviceDiv = document.getElementById("advice");
    
    try {
        // 显示思考过程
        thinkingDiv.style.display = "block";
        thinkingDiv.classList.remove("fade-out");
        thinkingDiv.classList.add("fade-in");
        reasoningDiv.textContent = "AI正在分析您的症状...";
        
        // 发送 AJAX 请求
        const response = await fetch("/get_advice", {
            method: "POST",
            body: new FormData(document.getElementById("conditionForm")),
        });
        const data = await response.json();
        
        if (data.error) {
            document.getElementById("error").textContent = data.error;
            document.getElementById("error").style.display = "block";
            thinkingDiv.style.display = "none";
            return;
        }
        
        // 显示推理内容
        reasoningDiv.textContent = data.reasoning || "无推理过程";
        
        // 等待2秒后淡出思考内容，显示结果
        setTimeout(() => {
            thinkingDiv.classList.remove("fade-in");
            thinkingDiv.classList.add("fade-out");
            setTimeout(() => {
                thinkingDiv.style.display = "none";
                resultDiv.style.display = "block";
                resultDiv.classList.add("fade-in");
                conditionResult.textContent = data.condition;
                adviceDiv.textContent = data.advice;
            }, 1000); // 等待淡出动画完成
        }, 2000); // 显示推理内容2秒
    } catch (error) {
        document.getElementById("error").textContent = "请求失败：" + error.message;
        document.getElementById("error").style.display = "block";
        thinkingDiv.style.display = "none";
    }
});
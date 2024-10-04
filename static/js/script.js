async function startEditing() {
    const inputText = document.getElementById("inputText").value;
    const userPrompt = document.getElementById("userPrompt").value;
    const outputContainer = document.getElementById("outputContainer");
    const loadingSpinner = document.getElementById("loading");
    const button = document.querySelector(".start-button");

    // Clear previous results
    outputContainer.innerHTML = '';

    // Show the loading spinner
    loadingSpinner.style.display = 'block';
    button.style.backgroundColor = "#f67e68"
    
    const data = {
        text: inputText,
        user_prompt: userPrompt
    };

    try {
        const response = await fetch("/edit_text", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data)
        });

        // Hide the loading spinner once the response is ready
        loadingSpinner.style.display = 'none';
    

        if (response.ok) {
            const apiResponse = await response.json();

            // Render each result
            apiResponse.forEach(result => {
                const card = document.createElement("div");
                card.classList.add("output-card");

                const original = document.createElement("p");
                original.classList.add("revision-original");
                original.textContent = "Original: " + result.original_sentence;
                card.appendChild(original);

                const revised = document.createElement("p");
                revised.classList.add("revision-revised");
                revised.textContent = "Revised: " + (result.revised_sentence || "No revision needed.");
                card.appendChild(revised);

                const explanation = document.createElement("p");
                explanation.classList.add("revision-explanation");
                explanation.textContent = "Explanation: " + (result.explanation || "No issues found.");
                card.appendChild(explanation);

                outputContainer.appendChild(card);
            });
        } else {
            console.error("Failed to fetch data");
        }
    } catch (error) {
        // Hide the loading spinner in case of error
        loadingSpinner.style.display = 'none';
        console.error("Error:", error);
    }
}

const wordLimit = 1000;

function updateWordCount() {
    const inputText = document.getElementById("inputText");
    const wordCountDisplay = document.getElementById("wordCount");
    const startButton = document.querySelector(".start-button");

    // Get the current word count
    const words = inputText.value.trim().split(/\s+/).filter(Boolean);
    const wordCount = words.length;

    // Display the current word count
    wordCountDisplay.textContent = `${wordCount}/${wordLimit} words`;

    // If the word count exceeds the limit, change color to red and disable button
    if (wordCount > wordLimit) {
        wordCountDisplay.style.color = "red";
        startButton.disabled = true;
        startButton.style.backgroundColor = "#ccc";  // Gray background for disabled button
        startButton.style.cursor = "not-allowed";    // Change cursor to indicate it's disabled
    } else {
        wordCountDisplay.style.color = "";           // Reset color
        startButton.disabled = false;
        startButton.style.backgroundColor = "#F4A896"; // Normal background color
        startButton.style.cursor = "pointer";        // Normal pointer
    }
}
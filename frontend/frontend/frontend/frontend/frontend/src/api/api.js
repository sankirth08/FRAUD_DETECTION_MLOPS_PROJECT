const API_URL = "http://127.0.0.1:8000";

export async function checkApiHealth() {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
    }
    return await response.json();
}

export async function predictFraud(transaction) {
    const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(transaction)
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
    }

    return await response.json();
}


const BASE_URL = "http://100.97.51.84:8000";

export async function getSessions(year = 2025) {
    const resp = await fetch(`${BASE_URL}/sessions?year=${year}`);
    return resp.json();
}

export async function getLaps(sessionKey) {
    const resp = await fetch(`${BASE_URL}/laps/${sessionKey}`);
    return resp.json();
}

export async function getPositions(sessionKey) {
    const resp = await fetch(`${BASE_URL}/positions/${sessionKey}`);
    return resp.json();
}

export async function getTelemetry(sessionKey) {
    const resp = await fetch(`${BASE_URL}/telemetry/${sessionKey}`);
    return resp.json();
}

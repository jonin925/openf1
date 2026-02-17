import { useState } from "react";
import SessionList from "./components/SessionList";
import LapTable from "./components/LapTable";
import PositionsTable from "./components/PositionsTable";
import TelemetryChart from "./components/TelemetryChart";

function App() {
    const [selectedSession, setSelectedSession] = useState(null);

    return (
        <div>
            <h1>OpenF1 Dashboard</h1>
            <SessionList onSelect={setSelectedSession} />
            
            {selectedSession && (
                <>
                    <LapTable sessionKey={selectedSession} />
                    <PositionsTable sessionKey={selectedSession} />
                    <TelemetryChart sessionKey={selectedSession} />
                </>
            )}
        </div>
    );
}

export default App;

import { useEffect, useState } from "react";
import { getSessions } from "../api/f1Api";

export default function SessionList({ onSelect }) {
    const [sessions, setSessions] = useState([]);

    useEffect(() => {
        getSessions().then(data => setSessions(data));
    }, []);

    return (
        <div>
            <h2>Sessions 2025</h2>
            <ul>
                {sessions.map(session => (
                    <li key={session.session_key} onClick={() => onSelect(session.session_key)}>
                        {session.meeting_name} - {session.session_name} ({session.date_start})
                    </li>
                ))}
            </ul>
        </div>
    );
}

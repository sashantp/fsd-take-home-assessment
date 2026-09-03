import { useEffect, useState } from "react";

function CalendarEvents() {
const [records, setRecords] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");


useEffect(() => {
    fetch("http://localhost:8000/events/calendar")
      .then((res) => res.json())
      .then((data) => setRecords(data));
  }, []);



return (
    <div>
      <h2>Calendar Events</h2>
      <ul>
        {records.map((record) => (
          <li key={record.event_id}>
            <strong>{record.title}</strong> 
            - {record.organizer} 
            - {record.start_time}
            - {record.description}
            - {record.location}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CalendarEvents;

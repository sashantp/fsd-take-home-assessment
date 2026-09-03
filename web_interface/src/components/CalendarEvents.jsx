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

      <table>
        <thead>
          <tr>
            <th>Id</th>
            <th>Title</th>
            <th>Organizer</th>
            <th>Start DateTime</th>
            <th>Location</th>
          </tr>
        </thead>

        <tbody>
          {records.map((record) => (
            <tr key={record.event_id}>
              <td>{record.event_id}</td>
              <td>{record.title}</td>
              <td>{record.organizer}</td>
              <td>{record.start_time}</td>
              <td>{record.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
);

}

export default CalendarEvents;

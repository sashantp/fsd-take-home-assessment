import { useEffect, useState } from "react";

function CrmEvents() {
const [records, setRecords] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");


useEffect(() => {
    fetch("http://localhost:8000/events/crm")
      .then((res) => res.json())
      .then((data) => setRecords(data));
  }, []);



return (
    <div>
      <h2>CRM Events</h2>
      <ul>
        {records.map((record) => (
          <li key={record.crm_id}>
            <strong>{record.subject}</strong> 
            - {record.client_name} 
            - {record.client_company}
            - {record.relationship_owner}
            - {record.meeting_date}
            - {record.meeting_time}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CrmEvents;

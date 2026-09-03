import { useEffect, useState } from "react";

function CrmReconciledEvents() {
const [records, setRecords] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");


useEffect(() => {
    fetch("http://localhost:8000/events/crm/reconciled")
      .then((res) => res.json())
      .then((data) => setRecords(data));
  }, []);


return (
    <div>
      <h2>CRM Events Reconciled</h2>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Subject</th>
            <th>Client Name</th>
            <th>Client Company</th>
            <th>Relationship Owner</th>
            <th>Meeting Date</th>
            <th>Meeting Time</th>
            <th>Calendar Event</th>
            <th>Difference</th>
          </tr>
        </thead>

        <tbody>
          {records.map((record) => (
            <tr key={record.crm_id}>
              <td>{record.crm_id}</td>
              <td>{record.subject}</td>
              <td>{record.client_name}</td>
              <td>{record.client_company}</td>
              <td>{record.relationship_owner}</td>
              <td>{record.meeting_date}</td>
              <td>{record.meeting_time}</td>
              <td>{record.event_id}</td>
              <td>{record.difference}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
);

}

export default CrmReconciledEvents;

import * as React from 'react';
import { useState, useEffect } from 'react';
import './styles.scss';

const Popup = () => {
  const [userInput, setUserInput] = useState('');
  const [submissions, setSubmissions] = useState<string[]>([]);
  const [displayData, setDisplayData] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  // Load submissions from local storage when the component mounts
  useEffect(() => {
    const savedSubmissions = localStorage.getItem('submissions');
    if (savedSubmissions) {
      setSubmissions(JSON.parse(savedSubmissions));
    }
  }, []);

  // Save submissions to local storage when they change
  useEffect(() => {
    localStorage.setItem('submissions', JSON.stringify(submissions));
  }, [submissions]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (userInput.trim() === '') {
      alert('Input is empty.');
      return;
    }
    setLoading(true);
    setSubmissions(prevSubmissions => [...prevSubmissions, userInput]);
    console.log('Data sent:', userInput);
    setUserInput(''); // Clear the input field
    setLoading(false);
  };

  const handleGenerateData = async () => {
    setLoading(true);
    setTimeout(() => {
      setDisplayData(submissions.map(s => s.toUpperCase()));
      setLoading(false);
    }, 500);
  };

  return (
    <section id="popup">
      <h2>Why did you open the website?</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Type your reason here"
          value={userInput}
          onChange={handleInputChange}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>Submit</button>
      </form>
      <div className="button-container">
        <button onClick={handleGenerateData} disabled={loading || submissions.length === 0}>
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </div>
      {!loading && displayData.length > 0 && (
        <div id="generated-data">
          <h3>Generated Data:</h3>
          <ul>
            {displayData.map((data, index) => (
              <li key={index}>{data}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
};

export default Popup;

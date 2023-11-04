import * as React from 'react';
import { useState, useEffect } from 'react';
import './styles.scss';

window.addEventListener('DOMContentLoaded', (event) => {
  // Inject the popup.html content
  fetch(chrome.runtime.getURL('popup.html'))
    .then(response => response.text())
    .then(data => {
      const div = document.createElement('div');
      div.innerHTML = data;
      document.body.appendChild(div);
      // Once added, you can now run scripts or attach events to the content
      const script = document.createElement('script');
      script.src = chrome.runtime.getURL('popup.js');
      script.onload = function() {
        this.remove();
      };
      (document.head || document.documentElement).appendChild(script);
    })
    .catch(err => console.error(err));
});

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
    // Add the new submission to the array of submissions
    setSubmissions(prevSubmissions => [...prevSubmissions, userInput]);
    console.log('Data sent:', userInput);
    setUserInput(''); // Clear the input field
    setLoading(false);
  };

  const handleGenerateData = async () => {
    setLoading(true);
    // Simulate an API call to generate data based on the submissions
    // This is where you would normally process the submissions
    // Here, we're simply converting them to uppercase
    setTimeout(() => {
      setDisplayData(submissions.map(s => s.toUpperCase())); // Convert to uppercase for display
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

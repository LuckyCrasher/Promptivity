import * as React from 'react';
import { useState, useRef } from 'react';
import { browser, Tabs } from 'webextension-polyfill-ts';

import './styles.scss';
import { unblockContent } from '../ContentScript/index';

function openWebPage(url: string): Promise<Tabs.Tab> {
  return browser.tabs.create({ url });
}

const sendEmail = (email: string): void => {
  const url = 'http://127.0.0.1:5000/sendmail';
  const data = { email };

  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(responseData => {
      console.log(responseData);
      if (responseData.is_valid) {
        unblockContent();
      }
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
};

const Popup: React.FC = () => {
  const [email, setEmail] = useState('');
  const emailRef = useRef<HTMLInputElement | null>(null);

  const handleSend = (e: React.FormEvent): void => {
    e.preventDefault();
    if (emailRef.current) {
      sendEmail(emailRef.current.value);
    }
  };

  return (
    <section id="popup">
      <h2>Promptivity</h2>
      <button
        id="github-button"
        type="button"
        onClick={(): Promise<Tabs.Tab> => {
          return openWebPage(
            'https://github.com/LuckyCrasher/Promptivity/tree/master'
          );
        }}
      >
        GitHub
      </button>
      <form id="email-form" onSubmit={handleSend}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Type your email here..."
          ref={emailRef}
        />
        <button type="submit">Send</button>
      </form>
    </section>
  );
};

export default Popup;

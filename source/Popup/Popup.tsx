import * as React from 'react';
import {browser, Tabs} from 'webextension-polyfill-ts';

import './styles.scss';
import {unblockContent} from '../ContentScript/prompt-blocker';

function openWebPage(url: string): Promise<Tabs.Tab> {
  return browser.tabs.create({url});
}

const Popup: React.FC = () => {
  const input = document.createElement('input');
  input.type = 'email';
  input.placeholder = 'Type your email here...';

  const button = document.createElement('button');
  button.onclick = (): void => {
    const url = 'http://127.0.0.1:5000/sendmail';
    const data = {
      email: input.value,
    };

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data), // Convert data to a JSON string
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json(); // Assuming the response is in JSON format
      })
      .then((responseData) => {
        console.log(responseData);
        if (responseData.is_valid) {
          unblockContent();
        }
      })
      .catch((error) => {
        console.error('There was a problem with the fetch operation:', error);
      });
  };

  // Wait for the DOM to be ready before accessing and manipulating it
  document.addEventListener('DOMContentLoaded', (): void => {
    const sendmailDiv = document.getElementById('sendmail');
    if (sendmailDiv) {
      sendmailDiv.appendChild(input);
      sendmailDiv.appendChild(button);
    }
  });

  return (
    <section id="popup">
      <h2>Promptivity</h2>
      {/* <button
        id="options__button"
        type="button"
        onClick={(): Promise<Tabs.Tab> => {
          return openWebPage('options.html');
        }}
      >
        Options Page
      </button> */}
      <div className="links__holder">
        <ul>
          <li>
            <button
              type="button"
              onClick={(): Promise<Tabs.Tab> => {
                return openWebPage(
                  'https://github.com/LuckyCrasher/Promptivity/tree/master'
                );
              }}
            >
              GitHub
            </button>
          </li>
          <li>
            <div id="sendmail" />
          </li>
        </ul>
      </div>
    </section>
  );
};

export default Popup;

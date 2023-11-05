// import {browser} from 'webextension-polyfill-ts';

let promptContainer: HTMLDivElement;
let promptStyle: HTMLStyleElement;
let title: HTMLDivElement
let sessionID = '';

function storeTimestamp(action: string): void {
  console.log('storing time stamp');
  console.log(action);
  const url = 'http://127.0.0.1:5000/new-record';
  const data = {
    sessionID,
    action,
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
    .catch((error) => {
      console.error('There was a problem with the fetch operation:', error);
    });
}

document.addEventListener('visibilitychange', () => {
  if (sessionID === '') return;
  if (document.hidden) {
    storeTimestamp('end');
  } else {
    storeTimestamp('start');
  }
});

function unblockContent(): void {
  // Remove the input field
  promptContainer.remove();

  promptStyle.innerHTML = '';

  // Reset window onscroll
  document.documentElement.setAttribute('style', 'overflow-y: auto !important');
  Array.from(document.getElementsByTagName('video')).forEach(
    (element): void => {
      element.volume = 100;
    }
  );
  Array.from(document.getElementsByTagName('audio')).forEach(
    (element): void => {
      element.volume = 100;
    }
  );
}

function validatePrompt(prompt: string): boolean {
  const url = 'http://127.0.0.1:5000/validate-reason';
  const data = {
    reason: prompt,
    url: document.baseURI,
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
        sessionID = responseData.sessionID;
        unblockContent();
      } else {
        title.textContent = responseData.reason;
      }
    })
    .catch((error) => {
      console.error('There was a problem with the fetch operation:', error);
    });
  return false;
}

function makePromptContainer(): HTMLDivElement {
  promptStyle = document.createElement('style');
  promptStyle.innerHTML = `
    .promptivity-overlay {
      position: absolute;
      top: 0;
      left: 0;
      bottom: 0;
      right: 0;
      z-index: 9999;
      backdrop-filter: blur(8px);
      display: flex;
      justify-content: center;
      align-items: center;
    }`;
  document.head.appendChild(promptStyle);

  const container = document.createElement('div');

  container.classList.add('promptivity-overlay');

  // Create a background container for the tab

  const tabBackground = document.createElement('div');
  tabBackground.style.backgroundColor = '#FF6666'; // Light red background color
  tabBackground.style.width = '100%';
  tabBackground.style.padding = '10px';
  tabBackground.style.borderRadius = '5px 5px 0 0';
  // Create a title for the popup

  title = document.createElement('div');
  title.textContent = 'Please tell us why you are visiting this website';
  title.style.fontSize = '18px';
  title.style.color = 'white'; // Text color
  // Create a text input field

  const inputField = document.createElement('input');
  inputField.type = 'text';
  inputField.placeholder = 'Type your reason here...';
  inputField.style.padding = '10px';
  inputField.style.fontSize = '16px';
  inputField.style.border = '2px solid #ccc';
  inputField.style.borderRadius = '0 0 5px 5px'; // Rounded bottom corners
  inputField.style.outline = 'none';
  inputField.style.width = '200px';
  inputField.style.marginRight = '5px';
  inputField.style.backgroundColor = 'white'; // White background
  // Create a submit button

  const submitButton = document.createElement('button');
  submitButton.type = 'button';
  submitButton.textContent = 'Submit';
  submitButton.style.padding = '10px 20px';
  submitButton.style.fontSize = '16px';
  submitButton.style.background = '#007bff'; // Blue background
  submitButton.style.color = 'white'; // Text color
  submitButton.style.border = 'none';
  submitButton.style.borderRadius = '5px';
  submitButton.style.cursor = 'pointer';
  // Add event listeners or functionality for the submit button as needed

  submitButton.addEventListener('click', (): void => {
    validatePrompt(inputField.value);
  });
  // Append the title and background to the background container

  tabBackground.appendChild(title);
  // Append the background container, input field, and submit button to the main container

  const centered = document.createElement('div');
  centered.appendChild(tabBackground);
  centered.appendChild(inputField);
  centered.appendChild(submitButton);

  container.appendChild(centered);

  // Append the container to the document body
  return container;
}

function shouldDisplayPopup(): boolean {
  // Check the current website's URL and decide whether to display the popup
  const currentURL = window.location.href;

  // Define an array of website URLs where you want to display the popup
  const allowedWebsites = [
    'https://www.netflix.com/ie/',
    'https://www.instagram.com/',
    'https://www.tiktok.com/',
    // Add more websites here
    // ...
  ];
  // Check if the currentURL matches any of the allowed websites
  return allowedWebsites.some((website) => currentURL.includes(website));
}

function blockContent(): void {
  if (shouldDisplayPopup()) {
    // Check tab active

    // make prompt container
    promptContainer = makePromptContainer();
    // Append the input field to the document body
    // Function to apply the blur overlay

    // Append the wrapper to the body
    document.body.appendChild(promptContainer);
    document.documentElement.setAttribute(
      'style',
      'overflow-y: hidden !important'
    );
    Array.from(document.getElementsByTagName('video')).forEach(
      (element): void => {
        element.volume = 0;
      }
    );
    Array.from(document.getElementsByTagName('audio')).forEach(
      (element): void => {
        element.volume = 0;
      }
    );
  }
}

blockContent();

export {blockContent, unblockContent};

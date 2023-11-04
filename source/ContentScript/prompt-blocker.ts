// import {browser} from 'webextension-polyfill-ts';

let inputField: HTMLInputElement;
let blurOverlay: HTMLDivElement;

function blockContent(): void {
  // Create a text input field
  inputField = document.createElement('input');
  inputField.type = 'text';
  inputField.placeholder = 'Type here...';
  inputField.style.position = 'fixed'; // Position it on top of the webpage
  inputField.style.top = '50%'; // Center vertically
  inputField.style.left = '50%'; // Center horizontally
  inputField.style.transform = 'translate(-50%, -50%)'; // Adjust for centering
  inputField.style.zIndex = '9999'; // Make sure it's on top of everything
  inputField.onsubmit = (): void => {
    console.log('Prompt submitted');
    console.log(inputField.value);
  };

  // Append the input field to the document body
  // Function to apply the blur overlay

  blurOverlay = document.createElement('div');
  blurOverlay.id = 'wrap-blur-overlay';

  // Move the body's children into this wrapper
  while (document.body.firstChild) {
    blurOverlay.appendChild(document.body.firstChild);
  }

  // Append the wrapper to the body
  blurOverlay.style.filter = 'blur(8px)';
  document.body.appendChild(blurOverlay);
  document.body.appendChild(inputField);
  const TopScroll = document.documentElement.scrollTop;
  const LeftScroll = document.documentElement.scrollLeft;

  window.onscroll = (): void => {
    window.scrollTo(LeftScroll, TopScroll);
  };
}

function unblockContent(): void {
  // Remove the input field
  inputField.remove();
  // Function to apply the blur overlay
  // Move the divs children back into body
  while (blurOverlay.firstChild) {
    document.body.appendChild(blurOverlay.firstChild);
  }
  // Remove the div
  blurOverlay.remove();
  // Reset window onscroll
  window.onscroll = (): void => {};
}

export {blockContent, unblockContent};

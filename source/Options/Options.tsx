import * as React from 'react';
import {StyledFirebaseAuth} from 'react-firebaseui';
import './styles.scss';
import {GoogleAuthProvider, getAuth} from 'firebase/auth';

const Options: React.FC = () => {
  // Firebase UI configuration
  const uiConfig = {
    signInFlow: 'popup',
    signInSuccessUrl: '/success', // Redirect to this URL after successful sign-in
    signInOptions: [GoogleAuthProvider.PROVIDER_ID],
    callbacks: {
      // Avoid redirects after sign-in
      signInSuccessWithAuthResult: () => false,
    },
  };

  return (
    <div>
      <h1>Options Page</h1>
      <p>Please sign in to continue:</p>
      <StyledFirebaseAuth uiConfig={uiConfig} firebaseAuth={getAuth()} />
    </div>
  );
};

export default Options;

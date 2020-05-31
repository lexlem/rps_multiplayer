import React, { Component } from 'react';
import styles from './styles.sass';

export class Timer extends Component {

  render() {
    return (
      <span>
        <span>Current round time left: </span>
        <span>
          {this.props.timer}
        </span>
      </span>
    )
  }
}

export default Timer;
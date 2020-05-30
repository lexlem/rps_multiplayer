import React, { Component } from 'react';
import CSSModules from 'react-css-modules';
import styles from './styles.sass';


class Lobby extends Component {
  state = {
    name: ''
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.setName(this.state.name);
    this.setState({ name: '' });
  }

  onChange = (e) => this.setState({ [e.target.name]: e.target.value });

  handleClick = () => {
    console.log('значение this:', this);
    this.props.connect();
  }

  render() {
    return (
      <div>
        <form onSubmit={this.onSubmit} style={{ display: 'flex' }}>
          <input
            type="text"
            name="name"
            style={{ flex: '10', padding: '5px' }}
            placeholder="Enter your name"
            value={this.state.name}
            onChange={this.onChange}
          />
          <input
            type="submit"
            value="Submit"
            className="btn"
            style={{ flex: '1' }}
          />
        </form>
        <button onClick={this.handleClick}>Play game!</button>
      </div>
    );
  }
}

export default CSSModules(Lobby, styles);
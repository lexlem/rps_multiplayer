import React, { Component } from 'react';
import './styles.sass';


export class Lobby extends Component {
  state = {
    name: this.props.playerName ? this.props.playerName : ""
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.setName(this.state.name);
    this.setState({ name: '' });
  }

  onChange = (e) => this.setState({ [e.target.name]: e.target.value });

  handleClick = () => {
    this.props.connect();
  }

  render() {
    return (
      <div className="Lobby">
        <h3>Start playing</h3>
        <form onSubmit={this.onSubmit} className="playerNameForm">
          <label htmlFor="name">Enter your name</label>
          <input
            type="text"
            id="name"
            name="name"
            placeholder="Enter your name"
            onChange={this.onChange}
          />
          <input
            type="submit"
            value="Submit"
            className="btn btn-primary"
          />
        </form>
        <button className="btn btn-primary" onClick={this.handleClick}>Play game!</button>
      </div>
    );
  }
}

export default Lobby;
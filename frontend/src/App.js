import React, { Component } from 'react'
import GameScene from './components/GameScene';
import Lobby from './components/Lobby';

import './App.sass';

class App extends Component {
  state = {
    playerProfile: {
      name: "",
      stats: {
        wins: 0,
        losses: 0,
        draws: 0,
        totalGames: 0
      }
    },
    ws: null
  };

  connect() {
    this.disconnect();
    var wsUri = "ws://localhost:8080";
    let conn = new WebSocket(wsUri);
    this.setState({ ws: conn });
    this.state.ws.onopen = function () {
      console.log('Queued.');
    };
    this.state.ws.onmessage = function (e) {
      console.log('Received: ' + e.data);
      if (e.data.action == "game_start") {

      } else if (e.data.action == "round_result") {

      } else if (e.data.action == "game_result") {

      }
    };
    this.state.ws.onclose = function () {
      console.log('Not queued.');
      this.setState({ ws: null });

    };
  }

  disconnect() {
    if (this.state.ws != null) {
      this.state.ws.close();
      this.setState({ ws: null });

    }
  }

  // // Toggle Complete
  // markComplete = id => {
  //   this.setState({
  //     todos: this.state.todos.map(todo => {
  //       if (todo.id === id) {
  //         todo.completed = !todo.completed;
  //       }
  //       return todo;
  //     })
  //   });
  // };

  // // Delete Todo
  // delTodo = id => {
  //   axios.delete(`https://jsonplaceholder.typicode.com/todos/${id}`).then(res =>
  //     this.setState({
  //       todos: [...this.state.todos.filter(todo => todo.id !== id)]
  //     })
  //   );
  // };

  // Set player name
  setName = name => {
    sessionStorage.setItem('rpsPlayerName', name);
    this.setState({ playerProfile: { ...this.state.playerProfile, name: name } });
  };

  render() {
    return (
      <div className="App">
        <div className="container">
          <Lobby
            playerProfile={this.state.playerProfile}
            ws={this.state.ws}
            setName={this.setName}
            connect={this.connect}
            disconnect={this.disconnect} />
          <GameScene playerProfile={this.state.playerProfile} ws={this.state.ws} />
        </div>
      </div>
    );
  }
}

export default App;
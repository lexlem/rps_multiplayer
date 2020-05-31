import React, { Component } from 'react'
import GameScene from './components/GameScene';
import Lobby from './components/Lobby';

import './App.sass';

class App extends Component {
  state = {
    isQueued: false,
    isPlayingGame: false,
    playerProfile: {
      name: sessionStorage.getItem('rpsPlayerName'),
      stats: {
        wins: sessionStorage.getItem('rpsPlayerWins') ? sessionStorage.getItem('rpsPlayerWins') : 0,
        losses: sessionStorage.getItem('rpsPlayerLosses') ? sessionStorage.getItem('rpsPlayerLosses') : 0,
        draws: sessionStorage.getItem('rpsPlayerDraws') ? sessionStorage.getItem('rpsPlayerDraws') : 0,
        totalGames: sessionStorage.getItem('rpsPlayerTotalGames') ? sessionStorage.getItem('rpsPlayerTotalGames') : 0
      }
    },
    ws: null,
    currentTimer: 0,
    results: {}
  };

  connect = () => {
    this.disconnect();
    var wsUri = "ws://localhost:8080";
    let conn = new WebSocket(wsUri);

    conn.onopen = () => {
      this.setState({ ws: conn, isQueued: true });
    };

    conn.onclose = e => {
      this.setState({ ws: null, isQueued: false });
    };

    conn.onerror = err => {
      console.error(
        "Socket encountered error: ",
        err.message,
        "Closing socket"
      );
      conn.close();
    };

    conn.onmessage = e => {
      let data = JSON.parse(e.data);
      console.log('Received: ' + data);
      if (data.action === "game_start") {
        this.setState({ isQueued: false, isPlayingGame: true });
      } else if (data.action === "round_result") {

      } else if (data.action === "timer") {
        this.setState({ currentTimer: data.message })
      } else if (data.action === "game_result") {
        this.setState({ isPlayingGame: false });
      }
    };
  }

  disconnect = () => {
    if (this.state.ws != null) {
      this.state.ws.close();
      this.setState({ ws: null });
    }
  }

  setName = name => {
    sessionStorage.setItem('rpsPlayerName', name);
    this.setState({ playerProfile: { ...this.state.playerProfile, name: name } });
  };

  onClickWeapon = weaponName => {
    this.state.ws.send(JSON.stringify({ "action": "choice", "message": weaponName }));
  };

  render() {
    const isQueued = this.state.isQueued;
    const isPlayingGame = this.state.isPlayingGame;
    let currentScene;
    if (isQueued) {
      currentScene = <div>Searching for opponents</div>
    } else if (isPlayingGame) {
      currentScene = <GameScene playerProfile={this.state.playerProfile} ws={this.state.ws} timer={this.state.currentTimer} onClickWeapon={this.onClickWeapon} results={this.state.results} />;
    } else {
      currentScene = <Lobby playerProfile={this.state.playerProfile} ws={this.state.ws} setName={this.setName} connect={this.connect} disconnect={this.disconnect} />;
    }

    return (
      <div className="App">
        <article className="container">
          <section className="profile">
            <h3>Your profile</h3>
            <p className="profileName">Your name: {this.state.playerProfile.name}</p>
            <div className="profileStats">
              <p>Wins: {this.state.playerProfile.stats.wins}</p>
              <p>Losses: {this.state.playerProfile.stats.losses}</p>
              <p>Draws: {this.state.playerProfile.stats.draws}</p>
            </div>
          </section>
          <section>
            {currentScene}
          </section>
        </article>
      </div>
    );
  }
}

export default App;
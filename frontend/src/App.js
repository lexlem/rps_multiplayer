import React, { Component } from 'react'
import { GameScene } from './components/GameScene';
import { Lobby } from './components/Lobby';
import { PlayerProfile } from './components/PlayerProfile';

import './App.sass';

class App extends Component {
  state = {
    isQueued: false,
    isPlayingGame: false,
    playerName: sessionStorage.getItem('rpsPlayerName') ? sessionStorage.getItem('rpsPlayerName') : "Player #" + this.getRandomInt(0, 32767),
    playerStats: {
      wins: sessionStorage.getItem('rpsPlayerWins') ? sessionStorage.getItem('rpsPlayerWins') : 0,
      losses: sessionStorage.getItem('rpsPlayerLosses') ? sessionStorage.getItem('rpsPlayerLosses') : 0,
      draws: sessionStorage.getItem('rpsPlayerDraws') ? sessionStorage.getItem('rpsPlayerDraws') : 0,
      totalGames: sessionStorage.getItem('rpsPlayerTotalGames') ? sessionStorage.getItem('rpsPlayerTotalGames') : 0
    },
    ws: null,
    currentTimer: 0,
    roundResult: null,
    roundPlayersChoices: [],
    gameResult: null,
  };

  getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  connect = () => {
    this.disconnect();
    var wsUri = "ws://localhost:8080";
    let conn = new WebSocket(wsUri);

    conn.onopen = () => {
      this.setState({ ws: conn, isQueued: true });
      if (this.state.playerName) {
        conn.send(JSON.stringify({ "action": "player_name", "message": this.state.playerName }));
      }
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
      if (data.action === "game_start") {
        this.setState({ isQueued: false, isPlayingGame: true });
      } else if (data.action === "round_result") {
        if (data.message.player_result === 1) {
          this.setState({ roundResult: "Win", roundPlayersChoices: data.message.all_players_choices })
        } else if (data.message.player_result === -1) {
          this.setState({ roundResult: "Loss", roundPlayersChoices: data.message.all_players_choices })
        } else {
          this.setState({ roundResult: "Draw", roundPlayersChoices: data.message.all_players_choices })
        }
      } else if (data.action === "timer") {
        this.setState({ currentTimer: data.message })
      } else if (data.action === "game_result") {
        if (data.message === "LOSE") {
          this.setState({ playerStats: { ...this.state.playerStats, losses: parseInt(this.state.playerStats.losses) + 1 } });
          sessionStorage.setItem('rpsPlayerLosses', parseInt(this.state.playerStats.losses));
        } else if (data.message === "WIN") {
          this.setState({ playerStats: { ...this.state.playerStats, wins: parseInt(this.state.playerStats.wins) + 1 } });
          sessionStorage.setItem('rpsPlayerWins', parseInt(this.state.playerStats.wins));
        } else {
          this.setState({ playerStats: { ...this.state.playerStats, draws: parseInt(this.state.playerStats.draws) + 1 } });
          sessionStorage.setItem('rpsPlayerDraws', parseInt(this.state.playerStats.draws));
        }
        this.setState({ playerStats: { ...this.state.playerStats, totalGames: parseInt(this.state.playerStats.totalGames) + 1 } });
        sessionStorage.setItem('rpsPlayerTotalGames', parseInt(this.state.playerStats.totalGames));
        setTimeout(
          function () {
            this.setState({ isPlayingGame: false, roundResult: null, gameResult: null });
            this.disconnect();
          }
            .bind(this),
          3000
        );
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
    this.setState({ playerName: name });
  };

  chooseWeapon = weaponName => {
    this.state.ws.send(JSON.stringify({ "action": "choice", "message": weaponName }));
  };

  forfeitGame = () => {
    this.state.ws.send(JSON.stringify({ "action": "forfeit" }));
    this.setState({ playerStats: { ...this.state.playerStats, losses: parseInt(this.state.playerStats.losses) + 1 } });
    sessionStorage.setItem('rpsPlayerLosses', parseInt(this.state.playerStats.losses));
    this.setState({ isPlayingGame: false, roundResult: null, gameResult: null });
  }

  render() {
    const isQueued = this.state.isQueued;
    const isPlayingGame = this.state.isPlayingGame;
    let currentScene;
    if (isQueued) {
      currentScene = <div>Searching for opponents</div>
    } else if (isPlayingGame) {
      currentScene = <GameScene
        playerName={this.state.playerName}
        playerStats={this.state.playerStats}
        ws={this.state.ws}
        timer={this.state.currentTimer}
        chooseWeapon={this.chooseWeapon}
        forfeitGame={this.forfeitGame}
        roundResult={this.state.roundResult}
        roundPlayersChoices={this.state.roundPlayersChoices}
        gameResult={this.state.gameResult} />;
    } else {
      currentScene = <Lobby
        playerName={this.state.playerName}
        playerStats={this.state.playerStats}
        ws={this.state.ws}
        setName={this.setName}
        connect={this.connect}
        disconnect={this.disconnect} />;
    }

    return (
      <div className="App">
        <article className="container">
          <section>
            <PlayerProfile
              playerName={this.state.playerName}
              playerStats={this.state.playerStats} />
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
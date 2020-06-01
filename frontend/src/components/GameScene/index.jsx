import React, { Component } from 'react';
import './styles.sass';

import WeaponList from "../WeaponList";
import Timer from "../Timer";
import Result from "../Result";

export class GameScene extends Component {

  render() {
    const roundResult = this.props.roundResult;
    let forfeitButton;
    if (!roundResult) {
      forfeitButton = (
        <button className="btn btn-danger" onClick={() => this.props.forfeitGame()}>Forfeit game</button>)
    }

    return (
      <div className="GameScene">
        <h3>Game</h3>
        <Timer timer={this.props.timer} />
        <WeaponList onClickWeapon={this.props.onClickWeapon} />
        <Result roundResult={this.props.roundResult} roundPlayersChoices={this.props.roundPlayersChoices} gameResult={this.props.gameResult} />
        {forfeitButton}
      </div>
    );
  }
}

export default GameScene;
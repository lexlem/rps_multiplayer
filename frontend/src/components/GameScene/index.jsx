import React, { Component } from 'react';
import './styles.sass';

import WeaponList from "../WeaponList";
import Timer from "../Timer";
import Result from "../Result";

export class GameScene extends Component {
 
  

  render() {
    return (
      <div className="GameScene">
        <h3>Game</h3>
        <Timer timer={this.props.timer} />
        <WeaponList onClickWeapon={this.props.onClickWeapon} />
        <Result results={this.props.results} />
      </div>
    );
  }
}

export default GameScene;
import React from 'react';
import './styles.sass';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHandRock, faHandPaper, faHandScissors } from '@fortawesome/free-solid-svg-icons'
import { Component } from 'react';

export class WeaponList extends Component {
  state = {
    weapons: [
      {
        id: "rock",
        icon: "faHandRock"
      },
      {
        id: "paper",
        icon: "faHandPaper"
      },
      {
        id: "scissors",
        icon: "faHandScissors"
      }
    ]
  }

  render() {
    return (
      <div className="WeaponList">
        <ul>
          <li>
            <button className="btn-weapon" onClick={() => this.props.onClickWeapon("rock")}>
              <FontAwesomeIcon icon={faHandRock} size="5x" />
            </button>
          </li>
          <li>
            <button className="btn-weapon" onClick={() => this.props.onClickWeapon("paper")}>
              <FontAwesomeIcon icon={faHandPaper} size="5x" />
            </button>
          </li>
          <li>
            <button className="btn-weapon" onClick={() => this.props.onClickWeapon("scissors")}>
              <FontAwesomeIcon icon={faHandScissors} size="5x" />
            </button>
          </li>
        </ul>
        <span className="label">CHOOSE A WEAPON</span>
      </div>
    )
  }
}

export default WeaponList;

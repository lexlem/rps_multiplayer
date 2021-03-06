import React from 'react';
import './styles.sass';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHandRock, faHandPaper, faHandScissors } from '@fortawesome/free-solid-svg-icons'
import { Component } from 'react';

export class WeaponList extends Component {
  render() {
    return (
      <div className="WeaponList">
        <ul>
          <li>
            <button className="btn-weapon" onClick={() => this.props.chooseWeapon("rock")}>
              <FontAwesomeIcon icon={faHandRock} size="5x" />
            </button>
          </li>
          <li>
            <button className="btn-weapon" onClick={() => this.props.chooseWeapon("paper")}>
              <FontAwesomeIcon icon={faHandPaper} size="5x" />
            </button>
          </li>
          <li>
            <button className="btn-weapon" onClick={() => this.props.chooseWeapon("scissors")}>
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

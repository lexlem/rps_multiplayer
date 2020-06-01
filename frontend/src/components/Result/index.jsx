import React, { Component } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHandRock, faHandPaper, faHandScissors } from '@fortawesome/free-solid-svg-icons'
import './styles.sass';

export class Result extends Component {

	state = {
		weapons: {
			"rock": <FontAwesomeIcon icon={faHandRock} size="3x" />,
			"paper": <FontAwesomeIcon icon={faHandPaper} size="3x" />,
			"scissors": <FontAwesomeIcon icon={faHandScissors} size="3x" />
		}
	}

	render() {
		const roundResult = this.props.roundResult;
		const roundPlayersChoicesBlock = Object.entries(this.props.roundPlayersChoices).map(([name, choice]) => {
			return <div key={name}>
				<div>{name}</div>
				<div>{this.state.weapons[choice]}</div>
			</div>
		});
		const gameResult = this.props.gameResult;
		let roundResultBlock, gameResultBlock;

		if (roundResult) {
			roundResultBlock = (<div className="round-results">
				<h4>Round results</h4>
				<div>
					{roundResult}
				</div>
				<div className="player-choices">
					{roundPlayersChoicesBlock}
				</div>
			</div>)
		}
		if (gameResult) {
			gameResultBlock = (<div className="game-results">
				<h4>Game results</h4>
				<div>
					{gameResult}
				</div>
			</div>
			)
		}

		return (
			<div className="Result">
				{roundResultBlock}
				{gameResultBlock}
			</div>

		)
	}
}

export default Result;
import React, { Component } from 'react';
import './styles.sass';

export class Result extends Component {

	render() {
		const roundResult = this.props.roundResult;
		const gameResult = this.props.gameResult;
		let roundResultBlock, gameResultBlock;

		if (roundResult) {
			roundResultBlock = (<div className="round-results">
				<h4>Round results</h4>
				<div>
					{roundResult}
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
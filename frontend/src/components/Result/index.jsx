import React, { Component } from 'react';
import styles from './styles.sass';

export class Result extends Component {

	render() {
		return (
			<div className="Result">
				{this.props.winner !== null && !this.props.loading && (
					<div className="winner">
						<span>
							{this.props.winner === 0 ? 'TIE' : `${(this.props.winner === 1)} WINS`}
						</span>
					</div>
				)}
				<div className="btn-play">
					<button
						disabled={this.props.loading}
						onClick={this.props.onClickPlay}
					>
						PLAY {(this.props.loading || this.props.winner !== null) && 'AGAIN'}
					</button>
				</div>
			</div>

		)
	}
}

export default Result;
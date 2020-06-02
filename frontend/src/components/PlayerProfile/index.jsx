import React, { Component } from 'react';
import './styles.sass';

export class PlayerProfile extends Component {
	state = {
		playerName: this.props.playerName,
		playerStats: this.props.playerStats
	}

	render() {
		return (
			<div className="profile">
				<h3>Your profile</h3>
				<p className="profileName">Your name: {this.state.playerName}</p>
				<div className="profileStats">
					<p>Total games: {this.state.playerStats.totalGames}</p>
					<p>Wins: {this.state.playerStats.wins}</p>
					<p>Losses: {this.state.playerStats.losses}</p>
					<p>Draws: {this.state.playerStats.draws}</p>
				</div>
			</div>
		)
	}
}

export default PlayerProfile;
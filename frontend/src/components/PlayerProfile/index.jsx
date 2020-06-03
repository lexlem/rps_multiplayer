import React, { Component } from 'react';
import './styles.sass';

export class PlayerProfile extends Component {

	render() {
		return (
			<div className="profile">
				<h3>Your profile</h3>
				<p className="profileName">Your name: {this.props.playerName}</p>
				<div className="profileStats">
					<p>Total games: {this.props.playerStats.totalGames}</p>
					<p>Wins: {this.props.playerStats.wins}</p>
					<p>Losses: {this.props.playerStats.losses}</p>
					<p>Draws: {this.props.playerStats.draws}</p>
				</div>
			</div>
		)
	}
}

export default PlayerProfile;
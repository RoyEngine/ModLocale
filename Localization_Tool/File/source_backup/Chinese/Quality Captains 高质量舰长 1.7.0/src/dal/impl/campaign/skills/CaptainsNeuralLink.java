package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.characters.LevelBasedEffect.ScopeDescription;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.impl.campaign.skills.NeuralLinkScript;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

public class CaptainsNeuralLink {
	
	public static int MAX_ELITE_SKILLS_BONUS = 1;
	
	public static boolean isNoOfficer(MutableShipStatsAPI stats) {
		if (stats.getEntity() instanceof ShipAPI) {
			ShipAPI ship = (ShipAPI) stats.getEntity();
//			if (ship == Global.getCombatEngine().getShipPlayerIsTransferringCommandFrom()) {
//				return false; // player is transferring command, no bonus until the shuttle is done flying
//				// issue: won't get called again when transfer finishes
//			}
			return ship.getCaptain().isDefault();
		} else {
			FleetMemberAPI member = stats.getFleetMember();
			if (member == null) return true;
			return member.getCaptain().isDefault();
		}
	}
	
	public static boolean isOriginalNoOfficer(MutableShipStatsAPI stats) {
		if (stats.getEntity() instanceof ShipAPI) {
			ShipAPI ship = (ShipAPI) stats.getEntity();
//			if (ship == Global.getCombatEngine().getShipPlayerIsTransferringCommandFrom()) {
//				return false; // player is transferring command, no bonus until the shuttle is done flying
//			}
			return ship.getOriginalCaptain() != null && ship.getOriginalCaptain().isDefault();
		} else {
			FleetMemberAPI member = stats.getFleetMember();
			if (member == null) return true;
			return member.getCaptain().isDefault();
		}
	}
	
	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			String control = Global.getSettings().getControlStringForEnumName(NeuralLinkScript.TRANSFER_CONTROL);
			String desc = Global.getSettings().getControlDescriptionForEnumName(NeuralLinkScript.TRANSFER_CONTROL);
			return "\n*使用 \"" + desc + "\" control [" + control + "] 即可在不同舰船之间进行切换。";
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			h = Misc.getDarkHighlightColor();
			return new Color[] {h};
		}
		public String[] getHighlights() {
			String control = Global.getSettings().getControlStringForEnumName(NeuralLinkScript.TRANSFER_CONTROL);
			String desc = Global.getSettings().getControlDescriptionForEnumName(NeuralLinkScript.TRANSFER_CONTROL);
			return new String [] {control};
		}
		public Color getTextColor() {
			return null;
		}
	}
	
	
	public static class Level1 extends BaseSkillEffectDescription implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			if (stats.isPlayerStats()) {
				stats.getDynamic().getMod(Stats.HAS_NEURAL_LINK).modifyFlat(id, 1f);
			}
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			if (stats.isPlayerStats()) {
				stats.getDynamic().getMod(Stats.HAS_NEURAL_LINK).unmodifyFlat(id);
			}
		}
		
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
				TooltipMakerAPI info, float width) {
			init(stats, skill);
			String dp = "" + (int)CaptainsNeuralLinkScript.INSTANT_TRANSFER_DP;
			
//			HullModSpecAPI modSpec = Global.getSettings().getHullModSpec(HullMods.NEURAL_INTERFACE);
//			HullModEffect e = modSpec.getEffect();
//			HullSize size = HullSize.CAPITAL_SHIP;
//			final String [] params = new String [] { 
//					 e.getDescriptionParam(0, size, null),
//					 e.getDescriptionParam(1, size, null),
//					 e.getDescriptionParam(2, size, null),
//					 e.getDescriptionParam(3, size, null),
//					 e.getDescriptionParam(4, size, null),
//					 e.getDescriptionParam(5, size, null),
//					 e.getDescriptionParam(6, size, null),
//					 e.getDescriptionParam(7, size, null),
//					 e.getDescriptionParam(8, size, null),
//					 e.getDescriptionParam(9, size, null)
//				};
//			info.addPara(modSpec.getDescription(size).replaceAll("\\%", "%%"), 0f, hc, hc, params);

			info.addPara("让两艘舰船能够同时受益于你个人的技能并且让你可以快速在两舰间切换。", hc, 0f);
			info.addPara("目标舰船不能在 军官 或 AI核心 的操控之下。", hc, 5f);
			//info.addSpacer(5f);
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level2 implements CharacterStatsSkillEffect {
		
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getDynamic().getMod(Stats.OFFICER_MAX_ELITE_SKILLS_MOD).modifyFlat(id, MAX_ELITE_SKILLS_BONUS);
		}
		
		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.OFFICER_MAX_ELITE_SKILLS_MOD).unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + Math.round(MAX_ELITE_SKILLS_BONUS) + " 军官可拥有 精英技能* 的上限";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.NONE;
		}
	}
}






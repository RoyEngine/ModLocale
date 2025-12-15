package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.LevelBasedEffect.ScopeDescription;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.util.Misc;

public class CaptainsOfficerManagement {
	
	public static float NUM_OFFICERS_BONUS = 2;
	public static float CP_BONUS = 2f;
	public static float MAX_ELITE_SKILLS_BONUS = 1;
	
	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			int baseOfficers = (int)Global.getSector().getPlayerStats().getOfficerNumber().getBaseValue();
			
			return "你所能指挥的最大军官人数基础为 " + baseOfficers + "}。";
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getDarkHighlightColor();
			return new Color[] {h};
		}
		public String[] getHighlights() {
			String baseOfficers = "" + (int)Global.getSector().getPlayerStats().getOfficerNumber().getBaseValue();
			return new String [] {baseOfficers};
		}
		public Color getTextColor() {
			return null;
		}
	}
	public static class Level1  implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getOfficerNumber().modifyFlat(id, NUM_OFFICERS_BONUS);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getOfficerNumber().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			//return "Able to command up to " + (int) (max) + " officers";
			return "+" + (int)NUM_OFFICERS_BONUS + " 至你能指挥的最大军官人数。";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.NONE;
		}
	}
	
	public static class Level1B implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getCommandPoints().modifyFlat(id, CP_BONUS);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getCommandPoints().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + Math.round(CP_BONUS) + " 指挥点";
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
			return "+" + Math.round(MAX_ELITE_SKILLS_BONUS) + " 军官最大精英技能数量";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.NONE;
		}
	}
}

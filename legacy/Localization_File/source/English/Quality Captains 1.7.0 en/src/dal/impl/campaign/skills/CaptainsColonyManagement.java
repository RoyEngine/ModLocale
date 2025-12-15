package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.util.Misc;

public class CaptainsColonyManagement {
	
	public static int ADMINS = 1;
	public static int ADMINS_ELITE = 1;
	public static int COLONY_NUM_BONUS = 1;
//	public static int LEVEL_3_BONUS = 1;
	
	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			int baseAdmins = (int)Global.getSector().getPlayerStats().getAdminNumber().getBaseValue();
			int baseOutposts = (int)Global.getSector().getPlayerStats().getOutpostNumber().getBaseValue();
			
			String colonies = "座殖民地";
			String admins = "名行政官";
			if (baseOutposts == 1) colonies = "colony";
			if (baseAdmins == 1) admins = "administrator";
			
			return "最初你仅能指派 " + 
					baseAdmins + " " + admins + " 且可以亲自管理 " +
					baseOutposts + " " + colonies + ". " +
					"当然你也可以通过牺牲稳定性，来管理超过自身能力上限数量的殖民地。";
//			return "At a base level, able to personally govern " +
//					baseOutposts + " " + colonies + ". " +
//					"The maximum number of colonies can be" +
//					" exceeded at the cost of a stability penalty. Colonies governed by administrators " +
//					"do not count against your personal limit.";
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			h = Misc.getDarkHighlightColor();
			return new Color[] {h, h, h};
		}
		public String[] getHighlights() {
			String baseAdmins = "" + (int)Global.getSector().getPlayerStats().getAdminNumber().getBaseValue();
			String baseOutposts = "" + (int)Global.getSector().getPlayerStats().getOutpostNumber().getBaseValue();
			return new String [] {baseAdmins, baseOutposts};
		}
		public Color getTextColor() {
			return null;
		}
	}
	

	public static class Level1 implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getOutpostNumber().modifyFlat(id, COLONY_NUM_BONUS);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getOutpostNumber().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "可以亲自管理额外 " + (int) COLONY_NUM_BONUS + " 座殖民地";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.NONE;
		}
	}
	
	public static class Level2 implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getAdminNumber().modifyFlat(id, ADMINS);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getAdminNumber().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "能够指派额外 " + (int) ADMINS + " 名行政官";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.NONE;
		}
	}
	
	//Custom elite
	public static class Level3 implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getAdminNumber().modifyFlat(id, ADMINS*2);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getAdminNumber().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "能够指派额外 " + (int)ADMINS_ELITE + " 名行政官";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.NONE;
		}
	}
	
	
//	public static class Level3A implements CharacterStatsSkillEffect {
//
//		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
//			stats.getOutpostNumber().modifyFlat(id, LEVEL_3_BONUS);
//		}
//
//		public void unapply(MutableCharacterStatsAPI stats, String id) {
//			stats.getOutpostNumber().unmodify(id);
//		}
//		
//		public String getEffectDescription(float level) {
//			int max = (int) Global.getSector().getCharacterData().getPerson().getStats().getOutpostNumber().getBaseValue();
//			max += LEVEL_2_BONUS;
//			max += LEVEL_3_BONUS;
//			
//			return "Able to personally govern up to " + (int) (max) + " colonies";
//			//return "Able to personally govern up to " + (int) (max) + " outposts";
//		}
//		
//		public String getEffectPerLevelDescription() {
//			return null;
//		}
//
//		public ScopeDescription getScopeDescription() {
//			return ScopeDescription.NONE;
//		}
//	}
}

package dal.impl.campaign.skills.milestones;

import java.awt.Color;
import java.io.IOException;

import com.fs.starfarer.BaseGameState;
import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI.SkillLevelAPI;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;
import com.fs.starfarer.combat.entities.BaseEntity;

public class CaptainsUsurper { //Usurpers, go figure
	
	public static boolean USE_AMBUSH = false;
	public static int BONUS_CONTACTS = 3;
	
	public static boolean enabled = false;
	public static final String skillID = "captains_usurper";
	public static final String skillName = "篡位者";
	public static final String skillDesc = "当我在我认为合适的时间和地点上取得胜利时，历史会免除掉我牺牲一两个星球的责任。";
	public static final String skillAuthor = "海军上将 Andrada，对霸主战略指挥部的致辞";
	public static final String skillIcon = "/graphics/icons/skills/"+ skillID + ".png";
	
	public static class Level1 implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			if (USE_AMBUSH) { 
				stats.getDynamic().getMod(Stats.CAN_DEPLOY_LEFT_RIGHT_MOD).modifyFlat(id, 1f);
			}
		}
		
		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.CAN_DEPLOY_LEFT_RIGHT_MOD).unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			if (enabled && USE_AMBUSH) {
				return "能够在任何战斗中从侧翼部署任意种类舰船";
			}
			return "";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			if (enabled && USE_AMBUSH) return ScopeDescription.FLEET;
			return ScopeDescription.NONE;
		}
	}
	
	public static class Level2 implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getDynamic().getMod(Stats.NUM_MAX_CONTACTS_MOD).modifyFlat(id, BONUS_CONTACTS);
		}
		
		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.NUM_MAX_CONTACTS_MOD).unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			if (enabled) {
				return "联络人上限增加 " + BONUS_CONTACTS;
			}
			return "";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			if (enabled) return ScopeDescription.NONE;
			return ScopeDescription.NONE;
		}
	}
		
	public static void toggleMilestone() {
		for (SkillLevelAPI skill : Global.getSector().getPlayerStats().getSkillsCopy()) {
			if (skill.getSkill().getId().equals(skillID)) {
				if (skill.getLevel()==0) {
					skill.getSkill().setDescription(skillDesc);
					skill.getSkill().setAuthor(skillAuthor);
					skill.getSkill().setName(skillName);
					try {
						Global.getSettings().loadTexture(skillIcon);
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName(skillIcon);
					//skill.getSkill().getTags().remove("npc_only");
					skill.getSkill().setPermanent(true);
					skill.setLevel(1);
					enabled = true;
				} else {
					skill.getSkill().setDescription("你只需不小心跌入蜘蛛网之中。");
					skill.getSkill().setAuthor("");
					skill.getSkill().setName("未来里程碑");
					try {
						Global.getSettings().loadTexture("graphics/icons/skills/blank.png");
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName("graphics/icons/skills/blank.png");				
					//skill.getSkill().addTag("npc_only");
					skill.getSkill().setPermanent(false);
					skill.setLevel(0);
					enabled = false;
				}
			}
		}
	}
	
	public static void enableDisable() {
		for (SkillLevelAPI skill : Global.getSector().getPlayerStats().getSkillsCopy()) {
			if (skill.getSkill().getId().equals(skillID)) {
				if (skill.getLevel() > 0) {
					skill.getSkill().setDescription(skillDesc);
					skill.getSkill().setAuthor(skillAuthor);
					skill.getSkill().setName(skillName);
					try {
						Global.getSettings().loadTexture(skillIcon);
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName(skillIcon);
					skill.getSkill().setPermanent(true);
					enabled = true;
				} else {
					skill.getSkill().setDescription("你只需不小心跌入蜘蛛网之中。");
					skill.getSkill().setAuthor("");
					skill.getSkill().setName("未来里程碑");
					try {
						Global.getSettings().loadTexture("graphics/icons/skills/blank.png");
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName("graphics/icons/skills/blank.png");				
					skill.getSkill().setPermanent(false);
					enabled = false;
				}
			}
		}
	}
}






package second_in_command.skills.automated

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.AICoreOfficerPlugin
import com.fs.starfarer.api.campaign.CampaignFleetAPI
import com.fs.starfarer.api.campaign.FleetDataAPI
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.AICoreOfficerPluginImpl
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.ids.Strings
import com.fs.starfarer.api.impl.campaign.ids.Tags
import com.fs.starfarer.api.impl.hullmods.Automated
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.SCUtils
import second_in_command.misc.SCSettings
import second_in_command.scripts.AutomatedShipsManager
import second_in_command.skills.technology.MakeshiftDrones
import second_in_command.specs.SCBaseSkillPlugin
import kotlin.math.roundToInt

class AutomatedShips : SCBaseAutoPointsSkillPlugin() {
    override fun getProvidedPoints(): Int {
        return (120 * SCSettings.autoPointsMult).toInt()
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        if (data.isNPC) {
            tooltip.addPara("允许舰队部署自动化舰船", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
            tooltip.addPara("自动化舰船只能由 AI 核心操控", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
            return
        }

        var manager = AutomatedShipsManager.get()
        var provided = getProvidedPoints()
        var maximum = manager.getMaximumDP()
        var used = manager.getUsedDP()
        tooltip.addPara("+$provided 无人舰点数", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("即使未占领任何目标点，仍能给予当前战斗规模 10%% 的部署点奖励", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        tooltip.addPara("如果空余无人舰点数大于零，就可以恢复自动化舰船", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("自动化舰船只能由 AI 核心操控", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        if (!data.isSkillActive(spec.id)) {
            maximum += provided
        }

        var bonus = SCUtils.computeThresholdBonus(used, manager.MAX_CR_BONUS, maximum)

        tooltip.addPara("+${bonus.toInt()}%% 战备值 (CR) 上限 (最高 ${manager.MAX_CR_BONUS.toInt()}%%) - 与同类技能共享 - 抵消内置船插降低 100%% 战备值的惩罚", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addPara("   - 当使用的无人舰点数少于自动化点数上限时达到最大效能", 0f,
            Misc.getTextColor(), Misc.getHighlightColor(), )

        tooltip.addPara("   - 包括本技能提供的点数在内，你的舰队的无人舰点数上限为 ${maximum.toInt()} ", 0f,
            Misc.getTextColor(), Misc.getHighlightColor(), "${maximum.toInt()}")

        tooltip.addPara("   - 你的舰队当前使用了 ${used.toInt()} 无人舰点数", 0f,
            Misc.getTextColor(), Misc.getHighlightColor(), "${used.toInt()}")

        tooltip.addSpacer(10f)

        val alpha = AICoreOfficerPluginImpl.ALPHA_MULT.roundToInt()
        val beta = AICoreOfficerPluginImpl.BETA_MULT.roundToInt()
        val gamma = AICoreOfficerPluginImpl.GAMMA_MULT.roundToInt()
        var label = tooltip.addPara("" +
                "总 \"无人舰点数\" 等于舰队中所有自动化舰船的部署点数，" +
                "再各自乘以安装的 AI 核心的倍率 - " +
                "Alpha 核心 ${alpha}${Strings.X}, " +
                "Beta 核心 ${beta}${Strings.X}, " +
                "Gamma 核心 ${gamma}${Strings.X}}。" +
	"由于安全联锁系统的限制，分配有 AI 核心的舰船{部署点数不受任何因素的影响}。", 0f,
            Misc.getGrayColor(), Misc.getHighlightColor())

        label.setHighlight("${alpha}${Strings.X}", "${beta}${Strings.X}", "${gamma}${Strings.X}", "部署点数不受任何因素的影响")
        label.setHighlightColors(Misc.getHighlightColor(), Misc.getHighlightColor(), Misc.getHighlightColor(), Misc.getNegativeHighlightColor())
    }

    override fun advance(data: SCData, amunt: Float?) {
        super.advance(data, amunt)

        if (data.isPlayer) {
            data.commander.stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MIN_FRACTION_OF_BATTLE_SIZE_BONUS_MOD)
                .modifyFlat(id, 0.1f)
        }


    }

    override fun onDeactivation(data: SCData) {
        super.onDeactivation(data)

        if (data.isPlayer) {
            data.commander.stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MIN_FRACTION_OF_BATTLE_SIZE_BONUS_MOD)
                .unmodify(id)
        }
    }
}